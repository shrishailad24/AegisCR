import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents, Polygon } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Navigation, Compass, AlertTriangle, Crosshair } from 'lucide-react';

// Fix Leaflet marker icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Helper component to center and pan the map smoothly
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom(), { animate: true, duration: 0.8 });
    }
  }, [center, zoom, map]);
  return null;
}
// Helper component to handle click events on the map
function MapEventsHandler({ onMapClick, onMapClickDrawing, isDrawingMode, onTempClick }) {
  useMapEvents({
    click(e) {
      if (isDrawingMode) {
        if (onMapClickDrawing) {
          onMapClickDrawing(e.latlng.lat, e.latlng.lng);
        }
      } else {
        if (onTempClick) {
          onTempClick(e.latlng.lat, e.latlng.lng);
        }
      }
    },
  });
  return null;
}

// Spherical/Flat-Earth Shoelace calculator for area estimation (in Sq Ft)
const calculatePolygonArea = (coords) => {
  if (coords.length < 3) return 0;
  const latToMeters = 111320; // approx meters per degree latitude
  const firstPoint = coords[0];
  const cosLat = Math.cos((firstPoint[0] * Math.PI) / 180);
  const lngToMeters = 111320 * cosLat; // approx meters per degree longitude
  
  const xyPoints = coords.map(c => ({
    x: (c[1] - firstPoint[1]) * lngToMeters,
    y: (c[0] - firstPoint[0]) * latToMeters
  }));
  
  let area = 0;
  for (let i = 0; i < xyPoints.length; i++) {
    const j = (i + 1) % xyPoints.length;
    area += xyPoints[i].x * xyPoints[j].y;
    area -= xyPoints[j].x * xyPoints[i].y;
  }
  area = Math.abs(area) / 2;
  
  // Convert square meters to square feet: 1 sqm = 10.76391 sqft
  return Math.round(area * 10.76391);
};

export default function PropertyMap({
  coordinates,
  onChangeCoordinates,
  selectedDistrict,
  selectedVillage,
  surveyNumber,
  valuationData,
  // GIS boundary polygon props
  polygonCoords = [],
  onPolygonChange,
  isDrawingMode = false,
  setIsDrawingMode,
  amenities = []
}) {
  const defaultCenter = [15.3173, 75.7139];
  const mapCenter = coordinates || defaultCenter;
  const zoomLevel = coordinates ? 15 : 7;

  const mapTilerKey = import.meta.env.VITE_MAPTILER_API_KEY || '';

  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState('');
  
  // Smart Property Selection state
  const [tempCoordinates, setTempCoordinates] = useState(null);

  // Clear temp selection when confirmed coordinates change
  useEffect(() => {
    if (coordinates) {
      setTempCoordinates(null);
    }
  }, [coordinates]);

  const handleConfirmLocation = () => {
    if (onChangeCoordinates && tempCoordinates) {
      onChangeCoordinates(tempCoordinates[0], tempCoordinates[1]);
    }
  };
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser.');
      return;
    }

    setGeoLoading(true);
    setGeoError('');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        if (onChangeCoordinates) {
          onChangeCoordinates(latitude, longitude);
        }
        setGeoLoading(false);
      },
      (error) => {
        console.error('Geolocation error:', error);
        setGeoError(
          error.code === 1
            ? 'Permission denied. Please enable location access.'
            : 'Position unavailable. Could not fetch location.'
        );
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  };

  const handleMapClickDrawing = (lat, lng) => {
    const newCoords = [...polygonCoords, [lat, lng]];
    const computedArea = calculatePolygonArea(newCoords);
    if (onPolygonChange) {
      onPolygonChange(newCoords, computedArea);
    }
  };

  const tileUrl = mapTilerKey
    ? `https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key=${mapTilerKey}`
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

  const attribution = mapTilerKey
    ? '&copy; <a href="https://www.maptiler.com/copyright" target="_blank">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
    : '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors';

  // Custom marker icon creation for schools, hospitals, banks
  const getAmenityIcon = (type) => {
    let color = '#22c55e'; // green default
    if (type === 'school') color = '#3b82f6'; // blue
    if (type === 'hospital') color = '#ef4444'; // red
    if (type === 'bank') color = '#eab308'; // yellow
    if (type === 'police' || type === 'police station') color = '#a855f7'; // purple
    if (type === 'market' || type === 'marketplace' || type === 'shop') color = '#f97316'; // orange
    if (type === 'fuel' || type === 'petrol pump') color = '#06b6d4'; // teal
    if (type === 'bus_stop' || type === 'bus stop') color = '#ec4899'; // pink
    
    return L.divIcon({
      html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2.5px solid white; box-shadow: 0 1px 4px rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center;"></div>`,
      className: 'custom-amenity-div-icon',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });
  };

  return (
    <div className="flex flex-col h-full w-full">
      {/* Warnings & Alerts */}
      {!mapTilerKey && (
        <div className="mb-2 bg-amber-500/10 border border-amber-500/30 rounded-xl p-2.5 flex items-center gap-2.5 text-amber-400 text-[11.5px]">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-500" />
          <span>
            <strong>MapTiler Key Missing:</strong> Running in fallback OpenStreetMap mode. Add{' '}
            <code className="bg-slate-900 px-1 py-0.5 rounded font-mono text-pink-400">VITE_MAPTILER_API_KEY</code> for high-resolution satellite imagery.
          </span>
        </div>
      )}

      {geoError && (
        <div className="mb-2 bg-rose-500/10 border border-rose-500/30 rounded-xl p-2.5 flex items-center gap-2.5 text-rose-400 text-[11.5px]">
          <AlertTriangle className="h-4 w-4 shrink-0 text-rose-500" />
          <span>{geoError}</span>
        </div>
      )}

      {/* Map Container */}
      <div className="flex-1 rounded-xl overflow-hidden border border-slate-800 shadow-inner relative z-0 min-h-[350px]">
        <MapContainer
          center={mapCenter}
          zoom={zoomLevel}
          style={{ height: '100%', width: '100%' }}
          zoomControl={true}
        >
          <TileLayer url={tileUrl} attribution={attribution} maxZoom={20} />
          
          <MapController center={mapCenter} zoom={zoomLevel} />
          <style>{`
            @keyframes pulse-ring {
              0% { transform: scale(0.9); opacity: 1; box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
              70% { transform: scale(1.1); opacity: 0.3; box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
              100% { transform: scale(0.9); opacity: 1; box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
            }
            .temp-marker-pulse {
              animation: pulse-ring 1.5s infinite;
              background-color: #f59e0b;
              width: 16px;
              height: 16px;
              border-radius: 50%;
              border: 2.5px solid white;
              box-shadow: 0 2px 6px rgba(0,0,0,0.5);
            }
          `}</style>

          <MapEventsHandler 
            onMapClick={onChangeCoordinates} 
            onMapClickDrawing={handleMapClickDrawing}
            isDrawingMode={isDrawingMode}
            onTempClick={setTempCoordinates}
          />

          {/* Render boundary polygon if points exist */}
          {polygonCoords.length > 0 && (
            <Polygon 
              positions={polygonCoords} 
              color="#10b981" 
              fillColor="#10b981" 
              fillOpacity={0.15} 
              weight={3} 
            />
          )}

          {/* Render polygon vertices as small dot markers */}
          {isDrawingMode && polygonCoords.map((coord, idx) => (
            <Marker 
              key={`vertex-${idx}`} 
              position={coord}
              icon={L.divIcon({
                html: `<div style="background-color: #10b981; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white;"></div>`,
                className: 'polygon-vertex-dot',
                iconSize: [10, 10],
                iconAnchor: [5, 5]
              })}
            />
          ))}

          {/* Unconfirmed temporary click marker */}
          {!isDrawingMode && tempCoordinates && (
            <Marker 
              position={tempCoordinates}
              icon={L.divIcon({
                html: `<div class="temp-marker-pulse"></div>`,
                className: 'temp-marker-div-icon',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
              })}
            >
              <Popup minWidth={200}>
                <div className="font-sans text-slate-800 p-1.5 text-center">
                  <h5 className="font-bold text-amber-600 text-xs mb-1">📍 Unconfirmed Location</h5>
                  <p className="text-[10px] text-slate-500 mb-2.5">
                    Coords: {tempCoordinates[0].toFixed(5)}, {tempCoordinates[1].toFixed(5)}
                  </p>
                  <button
                    type="button"
                    onClick={handleConfirmLocation}
                    className="w-full bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-1.5 px-3 rounded-lg text-[10.5px] transition duration-200"
                  >
                    Confirm Selection
                  </button>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Pin marker for selected coordinate */}
          {!isDrawingMode && coordinates && (
            <Marker position={coordinates}>
              <Popup minWidth={240}>
                <div className="font-sans text-slate-800 p-1">
                  <h4 className="font-bold text-sky-600 border-b border-slate-200 pb-1 mb-2 flex items-center gap-1.5 text-[13px]">
                    <Compass className="h-3.5 w-3.5" /> Pinned Appraisal Location
                  </h4>
                  <table className="w-full text-[11px] border-collapse">
                    <tbody>
                      {selectedDistrict && (
                        <tr className="border-b border-slate-100">
                          <td className="font-semibold py-1">District</td>
                          <td className="text-right py-1">{selectedDistrict}</td>
                        </tr>
                      )}
                      {selectedVillage && (
                        <tr className="border-b border-slate-100">
                          <td className="font-semibold py-1">Village</td>
                          <td className="text-right py-1">{selectedVillage}</td>
                        </tr>
                      )}
                      {surveyNumber && (
                        <tr className="border-b border-slate-100">
                          <td className="font-semibold py-1">Survey No</td>
                          <td className="text-right py-1">{surveyNumber}</td>
                        </tr>
                      )}
                      {valuationData ? (
                        <>
                          <tr className="border-b border-slate-100">
                            <td className="font-semibold py-1">Guideline Rate</td>
                            <td className="text-right py-1 text-emerald-600 font-bold">₹{valuationData.guidelineRate}/sqft</td>
                          </tr>
                          <tr className="border-b border-slate-100">
                            <td className="font-semibold py-1">AI Market Value</td>
                            <td className="text-right py-1 text-sky-600 font-bold">₹{valuationData.totalValue?.toLocaleString()}</td>
                          </tr>
                        </>
                      ) : (
                        <tr>
                          <td className="font-semibold py-1">Coords</td>
                          <td className="text-right py-1 font-mono">{coordinates[0].toFixed(5)}, {coordinates[1].toFixed(5)}</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Render GIS live amenities markers */}
          {!isDrawingMode && amenities.map((item, idx) => (
            <Marker 
              key={`amenity-${idx}`} 
              position={[item.lat, item.lon]} 
              icon={getAmenityIcon(item.type)}
            >
              <Popup>
                <div className="text-xs text-slate-800 p-0.5">
                  <span className="font-bold block capitalize text-sky-600 text-[11.5px]">{item.type}</span>
                  <span className="font-semibold block">{item.name || `Unnamed ${item.type}`}</span>
                  <span className="text-[10px] text-slate-400">Distance: {Math.round(item.distance)}m</span>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Sleek controls */}
      <div className="mt-4 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
        <div className="flex flex-col gap-0.5">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">🛰️ GIS Map Mode</span>
          <span className="text-xs font-mono font-bold text-slate-200">
            {isDrawingMode 
              ? `Boundary Mode: ${polygonCoords.length} vertices pinned`
              : coordinates 
                ? `${coordinates[0].toFixed(6)}° N , ${coordinates[1].toFixed(6)}° E`
                : 'No location pinned yet.'}
          </span>
        </div>
        <div className="flex gap-2 justify-end">
          {/* Select Property Button */}
          {!isDrawingMode && tempCoordinates && (
            <button
              type="button"
              onClick={handleConfirmLocation}
              className="bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-2 px-3.5 rounded-xl text-xs transition duration-300 shadow-md shadow-amber-500/20 flex items-center gap-1"
            >
              <span>📍 Select Property</span>
            </button>
          )}

          {!isDrawingMode && (
            <button
              type="button"
              onClick={handleUseMyLocation}
              disabled={geoLoading}
              className="flex items-center justify-center gap-1.5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 disabled:opacity-50 text-white font-bold py-2 px-3 rounded-xl text-xs transition duration-300"
            >
              {geoLoading ? (
                <div className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent" />
              ) : (
                <Navigation className="h-3.5 w-3.5 rotate-45" />
              )}
              <span>Locate</span>
            </button>
          )}

          {/* Polygon Drawing Toggle Button */}
          <button
            type="button"
            onClick={() => setIsDrawingMode(!isDrawingMode)}
            className={`flex items-center gap-1.5 font-bold py-2 px-3 rounded-xl text-xs transition duration-300 ${
              isDrawingMode
                ? 'bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-md shadow-amber-500/20'
                : 'bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700'
            }`}
          >
            <Crosshair className="h-3.5 w-3.5" />
            <span>{isDrawingMode ? 'Drawing Boundary...' : 'Draw Boundary'}</span>
          </button>
          
          {/* Clear Polygon Button */}
          {polygonCoords.length > 0 && (
            <button
              type="button"
              onClick={() => {
                if (onPolygonChange) onPolygonChange([], 0);
              }}
              className="bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 font-semibold py-2 px-3 rounded-xl text-xs transition duration-300"
            >
              Clear
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
