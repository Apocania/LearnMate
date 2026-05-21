import {
  DeleteOutlined,
  DownloadOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  LikeFilled,
  LikeOutlined,
  MessageOutlined,
  PlusOutlined,
  SendOutlined
} from "@ant-design/icons";
import { Alert, Button, Card, Input, List, Pagination, Popconfirm, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Course, listCourses } from "../api/courses";
import {
  ForumComment,
  ForumPost,
  createComment,
  deleteComment,
  deletePost,
  getForumAttachmentDownloadUrl,
  listComments,
  listPosts,
  togglePostLike,
  updatePostStatus
} from "../api/forum";
import { PageHeader } from "../components/PageHeader";
import { UserAvatar } from "../components/UserAvatar";
import { formatDate } from "../shared/utils/formatDate";
import { renderMarkdown } from "../shared/utils/markdown";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

const PAGE_SIZE = 10;

export function ForumPage() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [keyword, setKeyword] = useState("");
  const [statusFilter, setStatusFilter] = useState("active");
  const [commentsByPostId, setCommentsByPostId] = useState<Record<number, ForumComment[]>>({});
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});
  const [expandedPostId, setExpandedPostId] = useState<number | null>(null);
  const [expandedContentIds, setExpandedContentIds] = useState<Set<number>>(() => new Set());
  const [loadingCommentsPostId, setLoadingCommentsPostId] = useState<number | null>(null);
  const currentUser = useCurrentUser();
  const canDiscuss = Boolean(currentUser);
  const canManageForum = currentUser?.role === "mentor";

  async function refreshPosts(nextPage = page) {
    try {
      const result = await listPosts({
        course_id: selectedCourseId,
        keyword: keyword.trim(),
        status_filter: canManageForum ? statusFilter : "active",
        page: nextPage,
        page_size: PAGE_SIZE
      });
      setPosts(result.items);
      setTotal(result.total);
      setPage(result.page);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "帖子加载失败");
    }
  }

  async function refreshCourses() {
    try {
      setCourses(await listCourses());
    } catch {
      setCourses([]);
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
    void refreshCourses();
  }, []);

  useEffect(() => {
    void refreshPosts(1);
  }, [selectedCourseId, statusFilter]);

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

  async function handleTogglePostStatus(post: ForumPost) {
    try {
      await updatePostStatus(post.id, post.status === "hidden" ? "active" : "hidden");
      message.success(post.status === "hidden" ? "帖子已恢复" : "帖子已隐藏");
      await refreshPosts();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "状态更新失败");
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
      <Card className="toolbar-card">
        <Space wrap>
          <Select
            allowClear
            onChange={(value) => setSelectedCourseId(value ?? null)}
            options={courses.map((course) => ({ label: course.title, value: course.id }))}
            placeholder="按课程筛选"
            style={{ width: 220 }}
            value={selectedCourseId ?? undefined}
          />
          <Input.Search
            allowClear
            onChange={(event) => setKeyword(event.target.value)}
            onSearch={() => void refreshPosts(1)}
            placeholder="搜索标题或内容"
            style={{ width: 260 }}
            value={keyword}
          />
          {canManageForum ? (
            <Select
              onChange={setStatusFilter}
              options={[
                { label: "显示正常帖子", value: "active" },
                { label: "显示隐藏帖子", value: "hidden" },
                { label: "显示全部", value: "all" }
              ]}
              style={{ width: 160 }}
              value={statusFilter}
            />
          ) : null}
          <Button onClick={() => void refreshPosts(1)}>刷新</Button>
        </Space>
      </Card>
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
                    <Button
                      icon={post.status === "hidden" ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                      onClick={() => void handleTogglePostStatus(post)}
                      type="link"
                    >
                      {post.status === "hidden" ? "恢复" : "隐藏"}
                    </Button>
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
                      {post.course_id ? <Tag>{post.course_title ?? `课程 #${post.course_id}`}</Tag> : <Tag>通用讨论</Tag>}
                      {post.status === "hidden" ? <Tag color="red">已隐藏</Tag> : null}
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
        <Pagination
          className="forum-pagination"
          current={page}
          onChange={(nextPage) => void refreshPosts(nextPage)}
          pageSize={PAGE_SIZE}
          showSizeChanger={false}
          total={total}
        />
      </Card>
    </>
  );
}
