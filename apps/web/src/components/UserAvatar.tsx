import { UserOutlined } from "@ant-design/icons";
import { Avatar } from "antd";

import { resolveApiAssetUrl } from "../api/client";

type UserAvatarProps = {
  avatarUrl?: string | null;
  className?: string;
  size?: number;
  username?: string;
};

export function UserAvatar({ avatarUrl, className, size = 40, username }: UserAvatarProps) {
  const initial = username?.trim().slice(0, 1).toUpperCase();
  const src = resolveApiAssetUrl(avatarUrl);

  return (
    <Avatar className={className} icon={!initial ? <UserOutlined /> : undefined} size={size} src={src}>
      {!src && initial ? initial : null}
    </Avatar>
  );
}
