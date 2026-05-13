import { DeleteOutlined, LikeFilled, LikeOutlined, MessageOutlined, PlusOutlined, SendOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, Input, List, Modal, Popconfirm, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";

import {
  ForumComment,
  ForumPost,
  createComment,
  createPost,
  deleteComment,
  deletePost,
  listComments,
  listPosts,
  togglePostLike
} from "../api/forum";
import { PageHeader } from "../components/PageHeader";
import { UserAvatar } from "../components/UserAvatar";
import { formatDate } from "../shared/utils/formatDate";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type PostFormValues = {
  title: string;
  content: string;
};

export function ForumPage() {
  const [postForm] = Form.useForm<PostFormValues>();
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [commentsByPostId, setCommentsByPostId] = useState<Record<number, ForumComment[]>>({});
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});
  const [expandedPostId, setExpandedPostId] = useState<number | null>(null);
  const [loadingCommentsPostId, setLoadingCommentsPostId] = useState<number | null>(null);
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
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

  async function handleCreatePost(values: PostFormValues) {
    if (!canDiscuss) {
      message.info("请登录后再发布帖子");
      return;
    }
    try {
      const post = await createPost(values);
      message.success("帖子已发布");
      setIsPostModalOpen(false);
      postForm.resetFields();
      await refreshPosts();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "发帖失败");
    }
  }

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
          <Button disabled={!canDiscuss} icon={<PlusOutlined />} onClick={() => setIsPostModalOpen(true)} type="primary">
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
            <List.Item
              className="forum-post-item"
              actions={[
                <Button
                  disabled={!canDiscuss}
                  icon={post.liked_by_me ? <LikeFilled /> : <LikeOutlined />}
                  key="like"
                  onClick={() => void handleToggleLike(post)}
                  type="link"
                >
                  {post.like_count}
                </Button>,
                <Button
                  icon={<MessageOutlined />}
                  key="reply"
                  onClick={() => void handleToggleComments(post)}
                  type="link"
                >
                  {expandedPostId === post.id ? "收起评论" : `${post.comment_count} 评论`}
                </Button>,
                canManageForum ? (
                  <Popconfirm
                    key="delete"
                    okText="删除"
                    onConfirm={() => void handleDeletePost(post)}
                    title="确认删除这条帖子？"
                  >
                    <Button danger icon={<DeleteOutlined />} type="link">
                      删除
                    </Button>
                  </Popconfirm>
                ) : null
              ].filter(Boolean)}
            >
              <div className="forum-post-body">
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
                    <Space direction="vertical" size={6}>
                      <Space wrap split={<span>·</span>}>
                        <Typography.Text type="secondary">{post.author_name}</Typography.Text>
                        <Typography.Text type="secondary">{formatDate(post.created_at)}</Typography.Text>
                      </Space>
                      <Typography.Paragraph className="forum-post-content">{post.content}</Typography.Paragraph>
                    </Space>
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

      <Modal
        destroyOnHidden
        okText="发布"
        onCancel={() => setIsPostModalOpen(false)}
        onOk={() => postForm.submit()}
        open={isPostModalOpen}
        title="发布帖子"
      >
        <Form form={postForm} layout="vertical" onFinish={handleCreatePost}>
          <Form.Item label="标题" name="title" rules={[{ required: true, message: "请输入标题" }]}>
            <Input placeholder="请输入讨论标题" />
          </Form.Item>
          <Form.Item label="内容" name="content" rules={[{ required: true, message: "请输入内容" }]}>
            <Input.TextArea autoSize={{ minRows: 5, maxRows: 10 }} placeholder="描述问题、观点或学习心得" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
