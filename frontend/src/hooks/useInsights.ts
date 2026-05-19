import { useQuery } from "@tanstack/react-query";

import { insightsApi } from "@/services/insights";

export function useCountryInsights(country: string) {
  return useQuery({
    queryKey: ["insights", "by-country", country],
    queryFn: () => insightsApi.byCountry(country),
    enabled: country.length === 2,
  });
}

export function useCountryTitleAverages(country: string) {
  return useQuery({
    queryKey: ["insights", "by-country", country, "by-title"],
    queryFn: () => insightsApi.byCountryAndTitle(country),
    enabled: country.length === 2,
  });
}

export function useTopTitles(limit = 10) {
  return useQuery({
    queryKey: ["insights", "top-titles", limit],
    queryFn: () => insightsApi.topTitles(limit),
  });
}

export function useGlobalOverview() {
  return useQuery({
    queryKey: ["insights", "overview"],
    queryFn: () => insightsApi.overview(),
  });
}

export function useRecentEmployees(limit = 5) {
  return useQuery({
    queryKey: ["insights", "recent", limit],
    queryFn: () => insightsApi.recent(limit),
  });
}

export function useCountryDistribution() {
  return useQuery({
    queryKey: ["insights", "distribution"],
    queryFn: () => insightsApi.distribution(),
  });
}
