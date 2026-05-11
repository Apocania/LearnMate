import { DeleteOutlined, LikeFilled, LikeOutlined, MessageOutlined, PlusOutlined } from "@ant-design/icons";
import { Alert, Avatar, Button, Card, Form, Input, List, Modal, Popconfirm, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";

import {
  ForumComment,
  ForumPost,
  createComment,
  createPost,
  deletePost,
  listComments,
  listPosts,
  togglePostLike
} from "../api/forum";
import { PageHeader } from "../components/PageHeader";
import { getStoredCurrentUser } from "../shared/utils/currentUser";

type PostFormValues = {
  title: string;
  content: string;
};

type CommentFormValues = {
  content: string;
};

export function ForumPage() {
  const [postForm] = Form.useForm<PostFormValues>();
  const [commentForm] = Form.useForm<CommentFormValues>();
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [comments, setComments] = useState<ForumComment[]>([]);
  const [selectedPost, setSelectedPost] = useState<ForumPost | null>(null);
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const currentUser = getStoredCurrentUser();
  const canDiscuss = Boolean(currentUser);
  const canManageForum = currentUser?.role === "mentor";

  async function refreshPosts() {
    try {
      const nextPosts = await listPosts();
      setPosts(nextPosts);
      if (selectedPost) {
        setSelectedPost(nextPosts.find((post) => post.id === selectedPost.id) ?? null);
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : "帖子加载失败");
    }
  }

  async function refreshComments(postId: number) {
    try {
      setComments(await listComments(postId));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "评论加载失败");
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
      setSelectedPost(post);
      await refreshComments(post.id);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "发帖失败");
    }
  }

  async function handleSelectPost(post: ForumPost) {
    setSelectedPost(post);
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

  async function handleCreateComment(values: CommentFormValues) {
    if (!selectedPost) {
      return;
    }
    if (!canDiscuss) {
      message.info("请登录后再评论");
      return;
    }
    try {
      await createComment(selectedPost.id, values);
      commentForm.resetFields();
      await refreshComments(selectedPost.id);
      await refreshPosts();
      message.success("评论已发布");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "评论失败");
    }
  }

  async function handleDeletePost(post: ForumPost) {
    try {
      await deletePost(post.id);
      message.success("帖子已删除");
      if (selectedPost?.id === post.id) {
        setSelectedPost(null);
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
          dataSource={posts}
          renderItem={(post) => (
            <List.Item
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
                <Typography.Text key="reply">
                  <MessageOutlined /> {post.comment_count} 评论
                </Typography.Text>,
                <Button key="detail" onClick={() => void handleSelectPost(post)} type="link">
                  查看讨论
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
              <List.Item.Meta
                avatar={<Avatar>{post.author_name.slice(0, 1).toUpperCase()}</Avatar>}
                title={
                  <Space>
                    <Typography.Text strong>{post.title}</Typography.Text>
                    {post.course_id ? <Tag>课程 #{post.course_id}</Tag> : <Tag>通用讨论</Tag>}
                  </Space>
                }
                description={
                  <Space direction="vertical" size={4}>
                    <Typography.Text type="secondary">发起人：{post.author_name}</Typography.Text>
                    <Typography.Text>{post.content}</Typography.Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Modal
        footer={null}
        onCancel={() => setSelectedPost(null)}
        open={Boolean(selectedPost)}
        title={selectedPost?.title}
        width={720}
      >
        {selectedPost ? (
          <Space className="discussion-detail" direction="vertical" size="large">
            <Typography.Paragraph>{selectedPost.content}</Typography.Paragraph>
            <List
              dataSource={comments}
              header="评论"
              renderItem={(comment) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar>{comment.author_name.slice(0, 1).toUpperCase()}</Avatar>}
                    description={comment.content}
                    title={comment.author_name}
                  />
                </List.Item>
              )}
            />
            {canDiscuss ? (
              <Form form={commentForm} layout="vertical" onFinish={handleCreateComment}>
              <Form.Item name="content" rules={[{ required: true, message: "请输入评论内容" }]}>
                <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} placeholder="写下你的评论" />
              </Form.Item>
              <Button htmlType="submit" type="primary">
                发布评论
              </Button>
              </Form>
            ) : (
              <Alert message="登录后可以参与评论" showIcon type="info" />
            )}
          </Space>
        ) : null}
      </Modal>

      <Modal
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
