import { useEffect, useState } from "react";
import { ButtonToolbar, Input, Message, Modal, SelectPicker, Table, Tag } from "rsuite";

import Button from "../../atoms/Button/Button";
import { api } from "../../services/api";
import type { CaptionRequest } from "../../typings";

const { Column, HeaderCell, Cell } = Table;

interface RequestsTableProps {
  admin?: boolean;
}

export default function RequestsTable({ admin: isAdmin = false }: RequestsTableProps) {
  const [requests, setRequests] = useState<CaptionRequest[]>([]);
  const [status, setStatus] = useState(isAdmin ? "PENDING" : "");
  const [requestedBy, setRequestedBy] = useState("");
  const [selected, setSelected] = useState<CaptionRequest | null>(null);
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const result = isAdmin
      ? await api.approvalRequests(requestedBy, status)
      : await api.myRequests();
    setRequests(result.requests);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, [status, requestedBy]);

  async function review(request: CaptionRequest, nextStatus: string, rejectReason = "") {
    await api.reviewRequest(request.id, nextStatus, rejectReason);
    setSelected(null);
    setReason("");
    await load();
  }

  return (
    <>
      {isAdmin && (
        <div className="toolbar">
          <Input placeholder="Requested by email" value={requestedBy} onChange={setRequestedBy} />
          <SelectPicker
            searchable={false}
            cleanable={false}
            data={["PENDING", "APPROVED", "REJECTED"].map((value) => ({ label: value, value }))}
            value={status}
            onChange={(value) => setStatus(value || "PENDING")}
          />
        </div>
      )}

      {message && <Message type="error">{message}</Message>}

      <Table autoHeight data={requests} bordered cellBordered>
        <Column flexGrow={1.2}>
          <HeaderCell>Requested By</HeaderCell>
          <Cell dataKey="requested_by" />
        </Column>
        <Column flexGrow={1}>
          <HeaderCell>Tone</HeaderCell>
          <Cell dataKey="campaign_tone" />
        </Column>
        <Column flexGrow={2}>
          <HeaderCell>Caption</HeaderCell>
          <Cell>{(row) => row.generated_caption}</Cell>
        </Column>
        <Column width={130}>
          <HeaderCell>Status</HeaderCell>
          <Cell>
            {(row) => <Tag color={row.request_status === "APPROVED" ? "green" : row.request_status === "REJECTED" ? "red" : "orange"}>{row.request_status}</Tag>}
          </Cell>
        </Column>
        {!isAdmin && (
          <Column flexGrow={1}>
            <HeaderCell>Reject Reason</HeaderCell>
            <Cell>{(row) => row.request_reject_reason || "-"}</Cell>
          </Column>
        )}
        {isAdmin && (
          <Column width={190}>
            <HeaderCell>Action</HeaderCell>
            <Cell>
              {(row) =>
                row.request_status === "PENDING" ? (
                  <ButtonToolbar>
                    <Button size="xs" color="green" appearance="primary" onClick={() => review(row, "APPROVED")}>
                      Approve
                    </Button>
                    <Button size="xs" color="red" appearance="ghost" onClick={() => setSelected(row)}>
                      Reject
                    </Button>
                  </ButtonToolbar>
                ) : (
                  "-"
                )
              }
            </Cell>
          </Column>
        )}
      </Table>

      <Modal open={!!selected} onClose={() => setSelected(null)} size="xs">
        <Modal.Header>
          <Modal.Title>Reject Request</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Input as="textarea" rows={4} value={reason} onChange={setReason} placeholder="Reason is required" />
        </Modal.Body>
        <Modal.Footer>
          <Button appearance="primary" color="red" disabled={!reason.trim()} onClick={() => selected && review(selected, "REJECTED", reason)}>
            Reject
          </Button>
          <Button appearance="subtle" onClick={() => setSelected(null)}>
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
