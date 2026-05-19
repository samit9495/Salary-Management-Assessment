export type Employee = {
  id: number;
  full_name: string;
  job_title: string;
  country: string;
  salary: string;
  email: string | null;
  department: string | null;
  hire_date: string | null;
  is_active: boolean;
};

export type EmployeeCreate = {
  full_name: string;
  job_title: string;
  country: string;
  salary: string;
  email?: string | null;
  department?: string | null;
  hire_date?: string | null;
  is_active?: boolean;
};

export type EmployeeUpdate = Partial<EmployeeCreate>;

export type EmployeeListParams = {
  country?: string;
  q?: string;
  sort?: string;
  limit?: number;
  offset?: number;
};

export type CountryInsights = {
  country: string;
  average_salary: string;
  min_salary: string;
  max_salary: string;
  employee_count: number;
};

export type CountryTitleAverages = {
  country: string;
  averages: Record<string, string>;
};

export type TitleCount = {
  title: string;
  count: number;
};

export type TopTitles = {
  titles: TitleCount[];
};

export type GlobalOverview = {
  total_employees: number;
  average_salary: string;
  active_countries: number;
  active_titles: number;
};

export type CountryDistribution = {
  counts: Record<string, number>;
};
