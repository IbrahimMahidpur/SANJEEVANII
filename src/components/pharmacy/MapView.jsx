import React, { useState, useCallback, useRef, useEffect } from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPinIcon, MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/solid';

const libraries = ['places'];

const mapContainerStyle = {
  width: '100%',
  height: '600px',
};

const options = {
  disableDefaultUI: true,
  zoomControl: true,
  mapTypeControl: false,
  streetViewControl: false,
  styles: [
    {
      featureType: "poi",
      elementType: "labels",
      stylers: [{ visibility: "off" }]
    }
  ]
};

const MapView = () => {
  const [map, setMap] = useState(null);
  const [center, setCenter] = useState({ lat: 22.7196, lng: 75.8577 });
  const [markers, setMarkers] = useState([]);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [facilityType, setFacilityType] = useState('pharmacy');
  const [radius, setRadius] = useState(5000);
  const [isSearching, setIsSearching] = useState(false);
  const [showControls, setShowControls] = useState(true);

  const [userLocation, setUserLocation] = useState(null);

  const onLoad = useCallback((map) => {
    setMap(map);
  }, []);

  const searchNearby = useCallback(() => {
    if (!map) {
      console.error("Map not ready");
      return;
    }
    setIsSearching(true);
    setMarkers([]); // Clear previous markers

    const service = new window.google.maps.places.PlacesService(map);
    const request = {
      location: center,
      radius: radius,
      type: facilityType,
    };

    console.log("Searching nearby with request:", request);

    service.nearbySearch(request, (results, status) => {
      setIsSearching(false);
      console.log("Search status:", status, "Results:", results?.length || 0);

      if (status === window.google.maps.places.PlacesServiceStatus.OK && results) {
        setMarkers(results);
        console.log("Found", results.length, "places");
      } else if (status === window.google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
        alert("No " + facilityType + " found in this area. Try increasing the radius.");
      } else {
        console.error("Places API error:", status);
        alert("Search failed: " + status + ". Please check if Places API is enabled.");
      }
    });
  }, [map, center, radius, facilityType]);

  const handleMapClick = (e) => {
    setCenter({
      lat: e.latLng.lat(),
      lng: e.latLng.lng(),
    });
    setSelectedMarker(null);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newCenter = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setCenter(newCenter);
          setUserLocation(newCenter);
          map?.panTo(newCenter);
          map?.setZoom(15);
        },
        (error) => {
          console.error("Error getting location:", error);
          alert('Unable to retrieve your location. Please allow location access.');
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      );
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  };

  useEffect(() => {
    getCurrentLocation();
  }, [map]); // Try to get location once map is ready or on mount

  return (
    <div className="relative h-[600px] w-full group">
      {/* Controls Overlay */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md p-4 rounded-xl shadow-lg border border-white/20 w-80"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                <AdjustmentsHorizontalIcon className="w-5 h-5 text-primary-600" />
                Filters
              </h3>
              <button
                onClick={getCurrentLocation}
                className="text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded-md hover:bg-primary-100 transition-colors"
              >
                📍 My Location
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">Facility Type</label>
                <div className="grid grid-cols-3 gap-2 mt-1">
                  {['pharmacy', 'hospital', 'doctor'].map((type) => (
                    <button
                      key={type}
                      onClick={() => setFacilityType(type)}
                      className={`px-3 py-2 text-sm rounded-lg capitalize transition-all ${facilityType === type
                        ? 'bg-primary-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Search Radius</span>
                  <span>{radius / 1000} km</span>
                </div>
                <input
                  type="range"
                  min="1000"
                  max="10000"
                  step="1000"
                  value={radius}
                  onChange={(e) => setRadius(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                />
              </div>

              <button
                onClick={searchNearby}
                disabled={isSearching}
                className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSearching ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <MagnifyingGlassIcon className="w-5 h-5" />
                    Search Area
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <LoadScript
        googleMapsApiKey="AIzaSyCvqJa9gsbzxtG8EYwbK-ntmLl-kEMCH2w"
        libraries={libraries}
      >
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={14}
          onLoad={onLoad}
          onClick={handleMapClick}
          options={options}
        >
          <Marker
            position={center}
            icon="http://maps.google.com/mapfiles/ms/icons/red-dot.png"
            title="Map Center"
          />

          {userLocation && (
            <Marker
              position={userLocation}
              icon={{
                url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
                scaledSize: new window.google.maps.Size(40, 40)
              }}
              title="You are here"
              animation={window.google.maps.Animation.BOUNCE}
            />
          )}

          {markers.map((place, index) => (
            <Marker
              key={index}
              position={place.geometry.location}
              onClick={() => setSelectedMarker(place)}
              animation={window.google.maps.Animation.DROP}
            />
          ))}

          {selectedMarker && (
            <InfoWindow
              position={selectedMarker.geometry.location}
              options={{ maxWidth: 320, disableAutoPan: false }}
            >
              <div style={{ padding: '8px', minWidth: '280px', fontFamily: 'system-ui, sans-serif' }}>
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '18px'
                  }}>
                    {facilityType === 'pharmacy' ? '💊' : facilityType === 'hospital' ? '🏥' : '👨‍⚕️'}
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
                      {selectedMarker.name}
                    </h3>
                    <p style={{ margin: 0, fontSize: '12px', color: '#6b7280', textTransform: 'capitalize' }}>
                      {facilityType}
                    </p>
                  </div>
                </div>

                {/* Address */}
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ color: '#ef4444' }}>📍</span>
                  <p style={{ margin: 0, fontSize: '13px', color: '#4b5563', lineHeight: 1.4 }}>
                    {selectedMarker.vicinity}
                  </p>
                </div>

                {/* Rating & Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
                  {selectedMarker.rating && (
                    <span style={{
                      background: '#fef3c7',
                      color: '#92400e',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      ⭐ {selectedMarker.rating} ({selectedMarker.user_ratings_total || 0})
                    </span>
                  )}
                  {selectedMarker.opening_hours && (
                    <span style={{
                      background: selectedMarker.opening_hours.open_now ? '#d1fae5' : '#fee2e2',
                      color: selectedMarker.opening_hours.open_now ? '#065f46' : '#991b1b',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {selectedMarker.opening_hours.open_now ? '✅ Open Now' : '❌ Closed'}
                    </span>
                  )}
                  {selectedMarker.price_level !== undefined && (
                    <span style={{
                      background: '#e0e7ff',
                      color: '#3730a3',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {'₹'.repeat(selectedMarker.price_level || 1)}
                    </span>
                  )}
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '8px' }}>
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${selectedMarker.geometry.location.lat()},${selectedMarker.geometry.location.lng()}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      flex: 1,
                      padding: '10px',
                      background: 'linear-gradient(135deg, #667eea, #764ba2)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: '600',
                      textDecoration: 'none',
                      textAlign: 'center',
                      cursor: 'pointer'
                    }}
                  >
                    🧭 Get Directions
                  </a>
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedMarker.name)}&query_place_id=${selectedMarker.place_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      flex: 1,
                      padding: '10px',
                      background: '#f3f4f6',
                      color: '#374151',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: '600',
                      textDecoration: 'none',
                      textAlign: 'center',
                      cursor: 'pointer'
                    }}
                  >
                    📋 More Info
                  </a>
                </div>
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </LoadScript>
    </div>
  );
};

export default MapView;
