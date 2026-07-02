import React from "react";
import "./PropertyCard.css";

export interface Property {
  id: string;
  title: string;
  city: string;
  locality: string;
  bhk: number;
  price_inr: number;
  price_display: string;
  sqft: number;
  property_type: string;
  builder: string;
  possession: string;
  tags: string[];
  image_url?: string;
  lat?: number;
  lng?: number;
}

interface PropertyCardProps {
  property: Property;
  onViewLocation?: (property: Property) => void;
}

const PROPERTY_IMAGES = [
  "photo-1545324418-cc1a3fa10c00", // Apartment
  "photo-1512917774080-9991f1c4c750", // Modern villa
  "photo-1600585154340-be6161a56a0c", // Contemporary home
  "photo-1600596542815-ffad4c1539a9", // Villa exterior
  "photo-1600607687939-ce8a6c25118c", // Sleek apartment
  "photo-1564013799919-ab600027ffc6", // Luxury home
  "photo-1580587771525-78b9dba3b914", // Suburban house
  "photo-1513694203232-719a280e022f", // Modern townhouse
];

const getUnsplashImage = (id?: string) => {
  if (!id) return `https://images.unsplash.com/${PROPERTY_IMAGES[0]}?auto=format&fit=crop&w=120&h=120&q=80`;
  const num = parseInt(id.replace(/\D/g, "")) || 0;
  const index = num % PROPERTY_IMAGES.length;
  return `https://images.unsplash.com/${PROPERTY_IMAGES[index]}?auto=format&fit=crop&w=120&h=120&q=80`;
};

export default function PropertyCard({ property, onViewLocation }: PropertyCardProps) {
  const imageUrl = getUnsplashImage(property.id);

  return (
    <div className="property-card-horizontal">
      <div className="property-thumbnail-container">
        <img src={imageUrl} alt={property.title} className="property-thumbnail" />
        <span className="property-type-tag">{property.property_type}</span>
      </div>
      <div className="property-info-side">
        <div className="property-header-row">
          <h4 className="property-title-text">{property.title}</h4>
          <span className="property-price-text">{property.price_display}</span>
        </div>
        <p className="property-location-text">
          <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          {property.locality}, {property.city}
        </p>
        
        <div className="property-mini-specs">
          <span>{property.bhk} BHK</span>
          <span className="bullet-dot">•</span>
          <span>{property.sqft} sqft</span>
          <span className="bullet-dot">•</span>
          <span className="possession-status">{property.possession === "Ready to move" || property.possession === "Ready to Move" ? "Ready" : property.possession}</span>
        </div>

        <div className="property-card-footer">
          <span className="property-builder-text">By {property.builder}</span>
          {onViewLocation && (
            <button 
              className="btn-view-map-action" 
              onClick={(e) => {
                e.stopPropagation();
                onViewLocation(property);
              }}
            >
              View Location
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

