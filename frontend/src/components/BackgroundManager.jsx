import React, { useState, useEffect } from 'react';
import { useUnsplashBackground } from '../hooks/useUnsplashBackground';

/**
 * BackgroundManager component serves as a full-screen, responsive, blurred background
 * with a dynamic dark overlay and smooth cross-fade transition.
 */
export const BackgroundManager = ({ weatherMain = 'Clear', lat = 12.9716, lon = 77.5946 }) => {
  const { imageUrl, error } = useUnsplashBackground(weatherMain, lat, lon);
  const [activeUrl, setActiveUrl] = useState('');
  const [nextUrl, setNextUrl] = useState('');
  const [isCrossFading, setIsCrossFading] = useState(false);

  useEffect(() => {
    if (imageUrl) {
      if (!activeUrl) {
        // Initial load
        setActiveUrl(imageUrl);
      } else if (imageUrl !== activeUrl) {
        // Start cross-fade transition
        setNextUrl(imageUrl);
        setIsCrossFading(true);
        
        // Complete the fade animation (1.5 seconds transition)
        const timer = setTimeout(() => {
          setActiveUrl(imageUrl);
          setIsCrossFading(false);
          setNextUrl('');
        }, 1500);

        return () => clearTimeout(timer);
      }
    }
  }, [imageUrl, activeUrl]);

  return (
    <div style={containerStyle}>
      {/* Base Layer: Current active background image */}
      {activeUrl && (
        <div
          style={{
            ...backgroundImageStyle,
            backgroundImage: `url(${activeUrl})`,
            opacity: isCrossFading ? 0 : 1,
            transition: 'opacity 1.5s ease-in-out',
          }}
        />
      )}

      {/* Transition Layer: Slide/fade-in the new background image */}
      {isCrossFading && nextUrl && (
        <div
          style={{
            ...backgroundImageStyle,
            backgroundImage: `url(${nextUrl})`,
            opacity: 1,
            transition: 'opacity 1.5s ease-in-out',
          }}
        />
      )}

      {/* Dark Overlay Layer (35% to 45% transparency for readability) */}
      <div style={overlayStyle} />
    </div>
  );
};

// Inline styles for modularity, cleanliness, and responsiveness
const containerStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  zIndex: -999, // Render behind all dashboard content
  overflow: 'hidden',
  backgroundColor: '#0f172a', // Slate dark base background
};

const backgroundImageStyle = {
  position: 'absolute',
  top: '-20px', // Extra offset to hide edge artifacts from blur filter
  left: '-20px',
  right: '-20px',
  bottom: '-20px',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat',
  filter: 'blur(8px)', // Blur background slightly for readability
  transform: 'scale(1.05)', // Prevent white edges during blur
};

const overlayStyle = {
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  // Linear gradient with 38% to 43% dark slate overlay
  background: 'linear-gradient(rgba(15, 23, 42, 0.38), rgba(15, 23, 42, 0.43))',
  pointerEvents: 'none',
};

export default BackgroundManager;
