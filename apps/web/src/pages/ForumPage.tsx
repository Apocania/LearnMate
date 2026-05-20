import { DeleteOutlined, DownloadOutlined, LikeFilled, LikeOutlined, MessageOutlined, PlusOutlined, SendOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Input, List, Popconfirm, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  ForumComment,
  ForumPost,
  createComment,
  deleteComment,
  deletePost,
  getForumAttachmentDownloadUrl,
  listComments,
  listPosts,
  togglePostLike
} from "../api/forum";
import { PageHeader } from "../components/PageHeader";
import { UserAvatar } from "../components/UserAvatar";
import { formatDate } from "../shared/utils/formatDate";
import { renderMarkdown } from "../shared/utils/markdown";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

export function ForumPage() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [commentsByPostId, setCommentsByPostId] = useState<Record<number, ForumComment[]>>({});
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});
  const [expandedPostId, setExpandedPostId] = useState<number | null>(null);
  const [expandedContentIds, setExpandedContentIds] = useState<Set<number>>(() => new Set());
  const [loadingCommentsPostId, setLoadingCommentsPostId] = useState<number | null>(null);
  const currentUser = useCurrentUser();
  const canDiscuss = Boolean(currentUser);
  const canManageForum = currentUser?.role === "mentor";

  async function refreshPosts() {
    try {
      const nextPosts = await listPosts();
      setPosts(nextPosts);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "帖子加载失败");
    }
  }

  async function refreshComments(postId: number) {
    setLoadingCommentsPostId(postId);
    try {
      const nextComments = await listComments(postId);
      setCommentsByPostId((previous) => ({ ...previous, [postId]: nextComments }));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "评论加载失败");
    } finally {
      setLoadingCommentsPostId(null);
    }
  }

  useEffect(() => {
    void refreshPosts();
  }, []);

  async function handleToggleComments(post: ForumPost) {
    if (expandedPostId === post.id) {
      setExpandedPostId(null);
      return;
    }
    setExpandedPostId(post.id);
    await refreshComments(post.id);
  }

  async function handleToggleLike(post: ForumPost) {
    if (!canDiscuss) {
      message.info("请登录后再点赞");
      return;
    }
    try {
      await togglePostLike(post.id);
      await refreshPosts();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "点赞失败");
    }
  }

  function handleTogglePostContent(postId: number) {
    setExpandedContentIds((previous) => {
      const next = new Set(previous);
      if (next.has(postId)) {
        next.delete(postId);
      } else {
        next.add(postId);
      }
      return next;
    });
  }

  async function handleCreateComment(post: ForumPost) {
    if (!canDiscuss) {
      message.info("请登录后再评论");
      return;
    }
    const content = commentDrafts[post.id]?.trim();
    if (!content) {
      message.info("请输入评论内容");
      return;
    }
    try {
      await createComment(post.id, { content });
      setCommentDrafts((previous) => ({ ...previous, [post.id]: "" }));
      setExpandedPostId(post.id);
      await refreshComments(post.id);
      await refreshPosts();
      message.success("评论已发布");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "评论失败");
    }
  }

  async function handleDeleteComment(comment: ForumComment) {
    try {
      await deleteComment(comment.id);
      message.success("评论已删除");
      await refreshComments(comment.post_id);
      await refreshPosts();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "删除评论失败");
    }
  }

  async function handleDeletePost(post: ForumPost) {
    try {
      await deletePost(post.id);
      message.success("帖子已删除");
      if (expandedPostId === post.id) {
        setExpandedPostId(null);
      }
      await refreshPosts();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "删除帖子失败");
    }
  }

  return (
    <>
      <PageHeader title="讨论交流" description="和同学、伴学师一起提问、分享想法和完成答疑。" />
      {!currentUser ? (
        <Alert
          className="section-row"
          message="当前为游客浏览模式"
          description="你可以浏览帖子和评论；登录后可以发帖、点赞和评论，伴学师还可以管理交流区内容。"
          showIcon
          type="info"
        />
      ) : null}
      <Card
        extra={
          <Button disabled={!canDiscuss} icon={<PlusOutlined />} onClick={() => navigate("/forum/new")} type="primary">
            发布帖子
          </Button>
        }
        title="课程讨论"
      >
        <List
          className="forum-list"
          dataSource={posts}
          locale={{ emptyText: "暂无帖子" }}
          renderItem={(post) => (
            <List.Item className="forum-post-item">
              <div className="forum-post-body">
                {canManageForum ? (
                  <div className="forum-post-manage">
                    <Popconfirm
                      okText="删除"
                      onConfirm={() => void handleDeletePost(post)}
                      title="确认删除这条帖子？"
                    >
                      <Button danger icon={<DeleteOutlined />} type="link">
                        删除
                      </Button>
                    </Popconfirm>
                  </div>
                ) : null}
                <List.Item.Meta
                  avatar={<UserAvatar avatarUrl={post.author_avatar_url} size={44} username={post.author_name} />}
                  title={
                    <Space wrap>
                      <Typography.Text className="forum-post-title" strong>
                        {post.title}
                      </Typography.Text>
                      {post.course_id ? <Tag>课程 #{post.course_id}</Tag> : <Tag>通用讨论</Tag>}
                    </Space>
                  }
                  description={
                    (() => {
                      const isContentExpanded = expandedContentIds.has(post.id);
                      const shouldShowContentToggle = post.content.length > 220 || post.content.split(/\r?\n/).length > 5;

                      return (
                        <Space className="forum-post-summary" direction="vertical" size={6}>
                          <Space wrap split={<span>·</span>}>
                            <Typography.Text type="secondary">{post.author_name}</Typography.Text>
                            <Typography.Text type="secondary">{formatDate(post.created_at)}</Typography.Text>
                          </Space>
                          <div className={isContentExpanded ? "forum-post-excerpt expanded" : "forum-post-excerpt"}>
                            <div
                              className="forum-post-content markdown-preview"
                              dangerouslySetInnerHTML={{ __html: renderMarkdown(post.content) }}
                            />
                          </div>
                          <div className="forum-post-footer-row">
                            {post.attachments.length > 0 ? (
                              <Space className="forum-attachment-list" wrap>
                                {post.attachments.map((attachment) => (
                                  <Button
                                    href={getForumAttachmentDownloadUrl(attachment)}
                                    icon={<DownloadOutlined />}
                                    key={attachment.stored_name}
                                    target="_blank"
                                  >
                                    {attachment.original_name}
                                  </Button>
                                ))}
                              </Space>
                            ) : (
                              <span />
                            )}
                            <Space className="forum-post-actions" size={4}>
                              {shouldShowContentToggle ? (
                                <Button onClick={() => handleTogglePostContent(post.id)} type="link">
                                  {isContentExpanded ? "收起全文" : "展开全文"}
                                </Button>
                              ) : null}
                              <Button
                                disabled={!canDiscuss}
                                icon={post.liked_by_me ? <LikeFilled /> : <LikeOutlined />}
                                onClick={() => void handleToggleLike(post)}
                                type="link"
                              >
                                {post.like_count}
                              </Button>
                              <Button
                                icon={<MessageOutlined />}
                                onClick={() => void handleToggleComments(post)}
                                type="link"
                              >
                                {expandedPostId === post.id ? "收起评论" : `${post.comment_count} 评论`}
                              </Button>
                            </Space>
                          </div>
                        </Space>
                      );
                    })()
                  }
                />

                {expandedPostId === post.id ? (
                  <div className="post-comments-panel">
                    <List
                      className="post-comment-list"
                      dataSource={commentsByPostId[post.id] ?? []}
                      loading={loadingCommentsPostId === post.id}
                      locale={{ emptyText: "还没有评论，来写第一条吧" }}
                      renderItem={(comment) => (
                        <List.Item
                          actions={[
                            comment.can_delete ? (
                              <Popconfirm
                                key="delete"
                                okText="删除"
                                onConfirm={() => void handleDeleteComment(comment)}
                                title="确认删除这条评论？"
                              >
                                <Button danger icon={<DeleteOutlined />} type="link">
                                  删除
                                </Button>
                              </Popconfirm>
                            ) : null
                          ].filter(Boolean)}
                          className="post-comment-item"
                        >
                          <List.Item.Meta
                            avatar={
                              <UserAvatar
                                avatarUrl={comment.author_avatar_url}
                                size={34}
                                username={comment.author_name}
                              />
                            }
                            description={
                              <Space direction="vertical" size={3}>
                                <Typography.Paragraph className="post-comment-content">
                                  {comment.content}
                                </Typography.Paragraph>
                                <Typography.Text type="secondary">{formatDate(comment.created_at)}</Typography.Text>
                              </Space>
                            }
                            title={comment.author_name}
                          />
                        </List.Item>
                      )}
                    />
                    {canDiscuss ? (
                      <div className="comment-composer">
                        <UserAvatar
                          avatarUrl={currentUser?.avatar_url}
                          size={34}
                          username={currentUser?.username}
                        />
                        <Input.TextArea
                          autoSize={{ minRows: 2, maxRows: 5 }}
                          onChange={(event) =>
                            setCommentDrafts((previous) => ({ ...previous, [post.id]: event.target.value }))
                          }
                          placeholder="写下你的评论"
                          value={commentDrafts[post.id] ?? ""}
                        />
                        <Button
                          disabled={!commentDrafts[post.id]?.trim()}
                          icon={<SendOutlined />}
                          onClick={() => void handleCreateComment(post)}
                          type="primary"
                        >
                          发布
                        </Button>
                      </div>
                    ) : (
                      <Alert message="登录后可以参与评论" showIcon type="info" />
                    )}
                  </div>
                ) : null}
              </div>
            </List.Item>
          )}
        />
      </Card>
    </>
  );
}
