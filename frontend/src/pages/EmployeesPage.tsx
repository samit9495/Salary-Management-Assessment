import { useState } from "react";

import { EmployeeForm } from "@/components/EmployeeForm";
import { EmployeesFilters } from "@/components/EmployeesFilters";
import { EmployeesTable } from "@/components/EmployeesTable";
import { Pagination } from "@/components/Pagination";
import { ApiError } from "@/lib/api";
import {
  useCreateEmployee,
  useDeleteEmployee,
  useEmployees,
  useUpdateEmployee,
} from "@/hooks/useEmployees";
import type { Employee, EmployeeCreate, EmployeeListParams } from "@/services/types";

const DEFAULT_LIMIT = 25;

export function EmployeesPage() {
  const [page, setPage] = useState({ offset: 0, limit: DEFAULT_LIMIT });
  const [filters, setFilters] = useState<Omit<EmployeeListParams, "limit" | "offset">>({});
  const [editing, setEditing] = useState<Employee | null>(null);
  const [creating, setCreating] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const params: EmployeeListParams = { ...filters, ...page };
  const query = useEmployees(params);
  const createMutation = useCreateEmployee();
  const updateMutation = useUpdateEmployee();
  const deleteMutation = useDeleteEmployee();

  const handleApplyFilters = (next: Omit<EmployeeListParams, "limit" | "offset">) => {
    setFilters(next);
    setPage((p) => ({ ...p, offset: 0 }));
  };

  const handleCreate = async (payload: EmployeeCreate) => {
    setSubmitError(null);
    try {
      await createMutation.mutateAsync(payload);
      setCreating(false);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Failed to create employee");
    }
  };

  const handleUpdate = async (payload: EmployeeCreate) => {
    if (!editing) return;
    setSubmitError(null);
    try {
      await updateMutation.mutateAsync({ id: editing.id, payload });
      setEditing(null);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Failed to update employee");
    }
  };

  const handleDelete = async (employee: Employee) => {
    if (!window.confirm(`Delete ${employee.full_name}?`)) return;
    try {
      await deleteMutation.mutateAsync(employee.id);
    } catch (err) {
      if (err instanceof ApiError) setSubmitError(err.message);
    }
  };

  const rows = query.data ?? [];
  const isLastPage = rows.length < page.limit;

  return (
    <section aria-labelledby="employees-heading" className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 id="employees-heading" className="text-2xl font-semibold text-slate-900">
          Employees
        </h1>
        <button
          type="button"
          onClick={() => {
            setSubmitError(null);
            setCreating(true);
            setEditing(null);
          }}
          className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800"
        >
          New Employee
        </button>
      </header>

      <EmployeesFilters initial={filters} onApply={handleApplyFilters} />

      {creating || editing ? (
        <div className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="mb-3 text-base font-semibold text-slate-800">
            {editing ? `Edit ${editing.full_name}` : "New Employee"}
          </h2>
          <EmployeeForm
            initial={editing}
            submitLabel={editing ? "Save changes" : "Create"}
            submitError={submitError}
            onSubmit={editing ? handleUpdate : handleCreate}
            onCancel={() => {
              setCreating(false);
              setEditing(null);
              setSubmitError(null);
            }}
          />
        </div>
      ) : null}

      {query.isLoading ? (
        <p role="status" className="text-sm text-slate-500">
          Loading employees…
        </p>
      ) : query.isError ? (
        <p role="alert" className="text-sm text-red-700">
          Failed to load employees.
        </p>
      ) : (
        <EmployeesTable
          employees={rows}
          onEdit={(e) => {
            setEditing(e);
            setCreating(false);
            setSubmitError(null);
          }}
          onDelete={handleDelete}
        />
      )}

      <Pagination
        offset={page.offset}
        limit={page.limit}
        isLastPage={isLastPage}
        onChange={(next) => setPage(next)}
      />
    </section>
  );
}
