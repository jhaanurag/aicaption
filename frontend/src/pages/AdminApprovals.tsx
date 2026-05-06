import RequestsTable from "../organisms/RequestsTable/RequestsTable";

export default function AdminApprovals() {
  return (
    <div className="page">
      <h2>Caption Approval Requests</h2>
      <RequestsTable admin />
    </div>
  );
}
