export type UserRole = "student" | "mentor";

export type CurrentUser = {
  id: number;
  username: string;
  role: UserRole;
};
