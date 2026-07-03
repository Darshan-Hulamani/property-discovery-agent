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
  score?: number;
  score_reasons?: string[];
  bathrooms?: number;
  parking?: string;
  amenities?: string[];
  nearby_metro?: string;
  investment_score?: number;
  rental_yield_estimate?: string;
  ai_summary?: string;
}

interface PropertyCardProps {
  property: Property;
  onViewLocation?: (property: Property) => void;
}

function titleCase(value: string) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function PropertyCard({ property, onViewLocation }: PropertyCardProps) {
  const imageUrl = property.image_url || "/images/luxury_apartment_1_1783011988895.png";
  const hasLocation = typeof property.lat === "number" && typeof property.lng === "number";
  const reasons = property.score_reasons?.slice(0, 3) || [];
  const amenities = property.amenities?.slice(0, 3) || property.tags.slice(0, 3).map(titleCase);

  return (
    <article className="property-card-horizontal">
      <div className="property-thumbnail-container">
        <img src={imageUrl} alt={property.title} className="property-thumbnail" loading="lazy" />
        <span className="property-type-tag">{titleCase(property.property_type)}</span>
        {property.score !== undefined && <span className="property-score">{property.score}/100</span>}
      </div>

      <div className="property-info-side">
        <div className="property-header-row">
          <div>
            <h3 className="property-title-text">{property.title}</h3>
            <p className="property-location-text">{property.locality}, {property.city}</p>
          </div>
          <span className="property-price-text">{property.price_display}</span>
        </div>

        <div className="property-mini-specs" aria-label="Property specifications">
          <span>{property.bhk} BHK</span>
          <span>{property.bathrooms || property.bhk} Baths</span>
          <span>{property.sqft.toLocaleString("en-IN")} sqft</span>
          <span>{property.possession}</span>
        </div>

        {property.ai_summary && <p className="property-summary">{property.ai_summary}</p>}

        {reasons.length > 0 && (
          <ul className="score-reasons">
            {reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        )}

        <div className="amenity-row">
          {amenities.map((amenity) => (
            <span key={amenity}>{amenity}</span>
          ))}
        </div>

        <div className="property-card-footer">
          <div className="property-builder-text">
            <strong>{property.builder}</strong>
            <span>{property.nearby_metro || property.rental_yield_estimate || "Curated listing"}</span>
          </div>
          {onViewLocation && (
            <button
              className="btn-view-map-action"
              onClick={(e) => {
                e.stopPropagation();
                onViewLocation(property);
              }}
              disabled={!hasLocation}
            >
              Map
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
