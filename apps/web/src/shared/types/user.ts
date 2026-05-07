export type UserRole = "student" | "teacher" | "admin";

export type CurrentUser = {
  id: string;
  username: string;
  role: UserRole;
};

