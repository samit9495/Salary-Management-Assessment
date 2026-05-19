import { apiFetch } from "@/lib/api";
import type {
  CountryDistribution,
  CountryInsights,
  CountryTitleAverages,
  Employee,
  GlobalOverview,
  TopTitles,
} from "@/services/types";

export const insightsApi = {
  byCountry(country: string): Promise<CountryInsights> {
    return apiFetch<CountryInsights>(`/insights/by-country/${country}`);
  },
  byCountryAndTitle(country: string): Promise<CountryTitleAverages> {
    return apiFetch<CountryTitleAverages>(`/insights/by-country/${country}/by-title`);
  },
  topTitles(limit = 10): Promise<TopTitles> {
    return apiFetch<TopTitles>(`/insights/top-titles?limit=${limit}`);
  },
  overview(): Promise<GlobalOverview> {
    return apiFetch<GlobalOverview>(`/insights/overview`);
  },
  recent(limit = 5): Promise<Employee[]> {
    return apiFetch<Employee[]>(`/insights/recent?limit=${limit}`);
  },
  distribution(): Promise<CountryDistribution> {
    return apiFetch<CountryDistribution>(`/insights/distribution`);
  },
};
