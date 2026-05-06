import AdminApprovals from "./pages/AdminApprovals";
import AdminManageUsers from "./pages/AdminManageUsers";
import UserCreateCaption from "./pages/UserCreateCaption";
import UserPastRequests from "./pages/UserPastRequests";

export const routes = {
  "admin-users": AdminManageUsers,
  "admin-approvals": AdminApprovals,
  "create-caption": UserCreateCaption,
  "past-requests": UserPastRequests
};
