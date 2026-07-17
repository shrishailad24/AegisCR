import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom React Hook to fetch, cache, and manage dynamic nature background images from Unsplash or Pexels
 * based on weather conditions, time of day, and season.
 */
export const useUnsplashBackground = (weatherMain = 'Clear', lat = 12.9716, lon = 77.5946) => {
  const [imageUrl, setImageUrl] = useState('');
  const [nextImageUrl, setNextImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const recentIdsRef = useRef([]);
  const lastWeatherRef = useRef('');
  const lastTimeBucketRef = useRef('');
  const lastFetchTimeRef = useRef(0);

  // Read environment variables (do NOT expose secret key)
  const unsplashKey = process.env.REACT_APP_UNSPLASH_ACCESS_KEY || process.env.UNSPLASH_ACCESS_KEY || 'zRFlykNbtqwtGbs5CPWvvGRLxNK9xOmQwBsQ4X1Io1Q';
  const pexelsKey = process.env.REACT_APP_PEXELS_API_KEY || process.env.PEXELS_API_KEY || 'TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60';
  const fallbackLocalUrl = '/assets/loan_background_image.jpeg';

  // 1. Time of Day classification
  const getTimeOfDayBucket = useCallback(() => {
    const hour = new Date().getHours();
    if (5 <= hour && hour < 6) return 'Dawn';
    if (6 <= hour && hour < 7) return 'Sunrise';
    if (7 <= hour && hour < 11) return 'Morning';
    if (11 <= hour && hour < 13) return 'Noon';
    if (13 <= hour && hour < 16) return 'Afternoon';
    if (16 <= hour && hour < 18) return 'Golden Hour';
    if (18 <= hour && hour < 19) return 'Sunset';
    if (19 <= hour && hour < 21) return 'Evening';
    if (21 <= hour && hour < 23) return 'Night';
    return 'Midnight';
  }, []);

  // 2. Season classification
  const getSeasonBucket = useCallback(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const diff = now - start;
    const oneDay = 1000 * 60 * 60 * 24;
    const doy = Math.floor(diff / oneDay); // day of year

    if (60 <= doy && doy < 120) return 'Spring';
    if (120 <= doy && doy < 181) return 'Summer';
    if (181 <= doy && doy < 273) return 'Monsoon';
    if (273 <= doy && doy < 334) return 'Autumn';
    return 'Winter';
  }, []);

  // 3. Weather keyword mapping
  const getWeatherKeyword = useCallback((weather) => {
    const weatherKeywords = {
      Clear: ['sunrise mountains', 'green valley', 'crystal lake', 'alpine meadow', 'golden meadow', 'sunny beach'],
      Clouds: ['cloudy mountains', 'cloudy forest', 'cloudy valley', 'misty pine forest'],
      Rain: ['rainy forest', 'rainy mountains', 'rainforest', 'waterfall jungle', 'waterfall'],
      Drizzle: ['rainy forest', 'rainy mountains', 'rainforest', 'waterfall'],
      Thunderstorm: ['lightning landscape', 'storm clouds', 'dramatic sky'],
      Snow: ['snowy mountains', 'winter forest', 'frozen lake'],
      Mist: ['misty forest', 'fog valley', 'mountain fog', 'misty pine forest'],
      Haze: ['hazy hills', 'soft landscape'],
    };
    const options = weatherKeywords[weather] || ['mountains', 'green valley', 'crystal lake', 'forest'];
    return options[Math.floor(Math.random() * options.length)];
  }, []);

  // 4. Query Generator
  const generateQuery = useCallback((weather, timeOfDay, season) => {
    const weatherKw = getWeatherKeyword(weather);
    let baseQuery = '';
    
    if (['Night', 'Midnight'].includes(timeOfDay)) {
      baseQuery = `night stars ${weatherKw}`;
    } else if (['Sunset', 'Sunrise', 'Dawn', 'Golden Hour'].includes(timeOfDay)) {
      baseQuery = `${season.toLowerCase()} ${timeOfDay.toLowerCase()} ${weatherKw}`;
    } else {
      baseQuery = `${season.toLowerCase()} ${weatherKw}`;
    }

    return `${baseQuery} -people -person -interior -buildings -architecture`;
  }, [getWeatherKeyword]);

  // Fetch helper from Unsplash
  const fetchFromUnsplash = async (query) => {
    if (!unsplashKey) return null;
    const url = `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&orientation=landscape&per_page=15&client_id=${unsplashKey}`;
    
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (response.status === 200) {
          const data = await response.json();
          return data.results || [];
        } else if (response.status === 403) {
          break; // Rate limited
        }
      } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    }
    return null;
  };

  // Fetch helper from Pexels
  const fetchFromPexels = async (query) => {
    if (!pexelsKey) return null;
    const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&orientation=landscape&per_page=15`;
    
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const response = await fetch(url, {
          signal: controller.signal,
          headers: { 'Authorization': pexelsKey }
        });
        clearTimeout(timeoutId);
        if (response.status === 200) {
          const data = await response.json();
          const photos = data.photos || [];
          return photos.map(photo => ({
            id: `pexels_${photo.id}`,
            urls: {
              raw: photo.src.original,
              regular: photo.src.large2x
            }
          }));
        }
      } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    }
    return null;
  };

  // 5. Fetch Background logic
  const fetchBackground = useCallback(async (force = false) => {
    const now = Date.now();
    const timeOfDay = getTimeOfDayBucket();
    const season = getSeasonBucket();
    
    const weatherChanged = lastWeatherRef.current !== weatherMain;
    const timeChanged = lastTimeBucketRef.current !== timeOfDay;
    const timeExpired = (now - lastFetchTimeRef.current) >= 1800000;
    
    const shouldFetch = force || weatherChanged || timeChanged || timeExpired || !imageUrl;
    
    if (!shouldFetch) return;
    
    setIsLoading(true);
    setError(null);

    if (nextImageUrl && !force) {
      setImageUrl(nextImageUrl);
    }

    const query = generateQuery(weatherMain, timeOfDay, season);
    let results = await fetchFromUnsplash(query);

    // Fallback to Pexels if Unsplash fails/limits
    if (!results || results.length === 0) {
      console.log("Falling back to Pexels API in React Hook...");
      results = await fetchFromPexels(query);
    }

    if (results && results.length > 0) {
      const validImages = results.filter(img => !recentIdsRef.current.includes(img.id));
      const pool = validImages.length > 0 ? validImages : results;
      
      const selectedCurrent = pool[Math.floor(Math.random() * pool.length)];
      
      let currUrl = selectedCurrent.urls.raw;
      if (currUrl.includes('unsplash.com')) {
        currUrl += '&auto=format&fit=crop&w=3840&q=85';
      } else if (currUrl.includes('pexels.com')) {
        currUrl += '?auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85';
      }
      
      recentIdsRef.current.push(selectedCurrent.id);
      if (recentIdsRef.current.length > 10) {
        recentIdsRef.current.shift();
      }

      const remaining = pool.filter(img => img.id !== selectedCurrent.id);
      const selectedNext = remaining.length > 0 ? remaining[Math.floor(Math.random() * remaining.length)] : selectedCurrent;
      
      let nextUrl = selectedNext.urls.raw;
      if (nextUrl.includes('unsplash.com')) {
        nextUrl += '&auto=format&fit=crop&w=3840&q=85';
      } else if (nextUrl.includes('pexels.com')) {
        nextUrl += '?auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85';
      }

      if (!nextImageUrl || force) {
        setImageUrl(currUrl);
      }
      setNextImageUrl(nextUrl);

      lastWeatherRef.current = weatherMain;
      lastTimeBucketRef.current = timeOfDay;
      lastFetchTimeRef.current = now;
    } else {
      if (!imageUrl) {
        setError("Failed to fetch image from APIs. Using fallback.");
        setImageUrl(fallbackLocalUrl);
        setNextImageUrl(fallbackLocalUrl);
      }
    }
    
    setIsLoading(false);
  }, [weatherMain, generateQuery, getTimeOfDayBucket, getSeasonBucket, imageUrl, nextImageUrl]);

  useEffect(() => {
    fetchBackground();
  }, [fetchBackground]);

  useEffect(() => {
    if (nextImageUrl && !nextImageUrl.includes('data:')) {
      const img = new Image();
      img.src = nextImageUrl;
    }
  }, [nextImageUrl]);

  return { imageUrl, isLoading, error, refetch: () => fetchBackground(true) };
};
