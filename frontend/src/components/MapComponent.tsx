import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./MapComponent.css";
import { Property } from "./PropertyCard";

// Fix leaflet default marker icons issue with Webpack/Vite
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";

L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
});

// A component to center the map when properties change
function MapUpdater({ properties, activePropertyId, isOpen }: { properties: Property[], activePropertyId: string | null, isOpen: boolean }) {
  const map = useMap();

  useEffect(() => {
    // Invalidate size after the transition to make sure Leaflet resizes correctly
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 320); // 320ms to be safely just after the 300ms transition
    return () => clearTimeout(timer);
  }, [isOpen, map]);

  useEffect(() => {
    if (!isOpen) return;
    if (properties.length === 0) return;

    // Filter properties that have valid numeric lat/lng
    const validProps = properties.filter(p => 
      typeof p.lat === 'number' && typeof p.lng === 'number' && !isNaN(p.lat) && !isNaN(p.lng)
    );
    if (validProps.length === 0) return;

    const timer = setTimeout(() => {
      // Force Leaflet to update its size calculation before animating
      map.invalidateSize();

      if (activePropertyId) {
        const active = validProps.find(p => p.id === activePropertyId);
        if (active && active.lat && active.lng) {
          map.flyTo([active.lat, active.lng], 15, { duration: 1.5 });
          return;
        }
      }

      // Fit bounds to all valid properties
      const bounds = L.latLngBounds(validProps.map(p => [p.lat!, p.lng!]));
      map.flyToBounds(bounds, { padding: [50, 50], duration: 1.5 });
    }, 320); // 320ms to allow CSS transitions to finish and map dimensions to stabilize

    return () => clearTimeout(timer);

  }, [properties, activePropertyId, map, isOpen]);

  return null;
}

interface MapComponentProps {
  properties: Property[];
  activePropertyId: string | null;
  isOpen: boolean;
  onMarkerClick: (property: Property) => void;
}

export default function MapComponent({ properties, activePropertyId, isOpen, onMarkerClick }: MapComponentProps) {
  // Default to Bangalore center
  const center: [number, number] = [12.9716, 77.5946];
  
  return (
    <div className="map-container">
      <MapContainer center={center} zoom={11} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater properties={properties} activePropertyId={activePropertyId} isOpen={isOpen} />
        
        {properties.filter(p => typeof p.lat === 'number' && typeof p.lng === 'number' && !isNaN(p.lat) && !isNaN(p.lng)).map((prop) => (
          <Marker 
            key={prop.id} 
            position={[prop.lat!, prop.lng!]}
            eventHandlers={{
              click: () => onMarkerClick(prop),
            }}
          >
            <Popup>
              <div className="map-popup-content">
                <strong>{prop.title}</strong>
                <p>{prop.price_display}</p>
                <p>{prop.locality}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
