export interface Location {
  lat: number;
  lng: number;
}

export interface PharmacyLocation {
  id: string;
  name: string;
  address: string;
  location: Location;
  distance: number;
  rating: number | null;
  totalRatings: number;
  isOpen: boolean | null;
  types: string[];
  icon?: string;
  photos?: Photo[];
  phone?: string;
  website?: string;
  openingHours?: OpeningHours;
  reviews?: Review[];
}

export interface Photo {
  reference: string;
  width: number;
  height: number;
}

export interface OpeningHours {
  isOpen: boolean;
  weekdayText: string[];
}

export interface Review {
  author: string;
  rating: number;
  text: string;
  time: number;
}

export interface SearchFilters {
  type: 'pharmacy' | 'doctor' | 'hospital' | 'clinic' | 'all';
  radius: number;
  sortBy: 'distance' | 'rating';
  openNow: boolean;
}

export interface UserLocation {
  lat: number;
  lng: number;
  address?: string;
}

export interface NearbyResponse {
  results: PharmacyLocation[];
  count: number;
  searchLocation: Location;
  radius: number;
  type: string;
}

export interface PlaceDetailsResponse {
  id: string;
  name: string;
  address: string;
  phone: string | null;
  website: string | null;
  location: Location;
  rating: number | null;
  totalRatings: number;
  openingHours: OpeningHours | null;
  types: string[];
  photos: Photo[];
  reviews: Review[];
}

// Medicine Availability Types
export interface MedicineAvailability {
  pharmacyId: string;
  pharmacyName: string;
  pharmacyAddress: string;
  distance: number;
  location: Location;
  medicineName: string;
  available: boolean;
  confidence: number; // 0-1 score
  lastUpdated: string;
  source: 'pharmacy_api' | 'public_data' | 'crowdsourced';
  estimatedPrice?: {
    amount: string;
    currency: string;
  };
}

export interface MedicineInfo {
  id: string;
  name: string;
  synonym?: string;
  brandNames?: string[];
  genericName?: string;
  manufacturer?: string;
  dosageForm?: string;
  route?: string;
  type?: string;
}

export interface MedicineSearchResponse {
  query: string;
  results: MedicineInfo[];
  count: number;
}

export interface MedicineAvailabilityResponse {
  medicine: string;
  location: Location;
  radius: number;
  availability: MedicineAvailability[];
  totalPharmacies: number;
  availableCount: number;
}

// Distance Matrix Types
export interface DistanceMatrixElement {
  distance: {
    text: string;
    value: number;
  };
  duration: {
    text: string;
    value: number;
  };
  status: string;
}

export interface DistanceMatrixRow {
  elements: DistanceMatrixElement[];
}

export interface DistanceMatrixResponse {
  origins: Location[];
  destinations: Location[];
  rows: DistanceMatrixRow[];
}

// Autocomplete Types
export interface AutocompleteSuggestion {
  placeId: string;
  description: string;
  mainText?: string;
  secondaryText?: string;
  types: string[];
}

export interface AutocompleteResponse {
  input: string;
  suggestions: AutocompleteSuggestion[];
}

export interface MedicineAutocompleteSuggestion {
  term: string;
  suggestions: string[];
}
