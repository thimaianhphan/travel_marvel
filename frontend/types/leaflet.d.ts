declare module "leaflet" {
  export type Icon = any;
  export type DivIcon = any;

  export interface DivIconOptions {
    html?: string | HTMLElement;
    className?: string;
    iconSize?: [number, number] | [number, number][];
    iconAnchor?: [number, number];
  }

  export function divIcon(options?: DivIconOptions): DivIcon;

  const Leaflet: {
    divIcon: typeof divIcon;
  };

  export default Leaflet;
}

