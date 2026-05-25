import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.init_db import init_db
from app.core.security import get_password_hash
from app.modules.assistant.knowledge_ingestion import KnowledgeIngestionService
from app.modules.assistant.models import AssistantMessage, AssistantSession
from app.modules.auth.models import User
from app.modules.courses.models import Course, CourseChapter, CourseEnrollment
from app.modules.files.models import FileAsset
from app.modules.forum.models import ForumComment, ForumLike, ForumPost
from app.modules.learning_records.models import LearningEvent
from app.modules.messages.models import UserMessage

UPLOAD_DIR = ROOT / "storage" / "uploads"
PASSWORD = "password123"


def main() -> None:
  init_db()
  UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
  with SessionLocal() as db:
    users = seed_users(db)
    courses = seed_courses(db, users["mentor"])
    chapters = seed_chapters(db, courses)
    files = seed_files(db, users["mentor"], courses, chapters)
    posts = seed_forum(db, users, courses)
    seed_messages(db, users, posts)
    seed_assistant(db, users["student"], courses["space"])
    seed_learning_events(db, users["student"], users["mentor"], courses, files, posts)
    db.commit()
  print("Demo data is ready.")
  print("Accounts:")
  print(f"  student: demo_student / {PASSWORD}")
  print(f"  mentor : demo_mentor  / {PASSWORD}")


def seed_users(db):
  demo_users = {
    "student": ("demo_student", "student", "/static/avatars/demo-student.svg"),
    "mentor": ("demo_mentor", "mentor", "/static/avatars/demo-mentor.svg"),
    "star": ("star_reader", "student", "/static/avatars/star-reader.svg"),
  }
  result = {}
  for key, (username, role, avatar_url) in demo_users.items():
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
      user = User(username=username, role=role, password_hash=get_password_hash(PASSWORD), avatar_url=avatar_url)
      db.add(user)
      db.flush()
    else:
      user.role = role
      user.password_hash = get_password_hash(PASSWORD)
      user.avatar_url = avatar_url
    result[key] = user
  return result


def seed_courses(db, mentor: User):
  course_specs = {
    "space": (
      "星际数学探险",
      "把分数、图形和逻辑题变成一次星际任务，学生在闯关中理解数学概念。",
      "published",
    ),
    "science": (
      "奇妙科学实验室",
      "从彩虹、磁铁、空气和植物开始，观察现象、提出问题并记录实验发现。",
      "published",
    ),
    "reading": (
      "故事阅读与表达",
      "通过绘本、角色扮演和小小演讲，训练阅读理解、表达和同伴倾听。",
      "published",
    ),
    "python": (
      "Python 创意编程",
      "用简单代码画图、做互动小游戏，建立计算思维和作品表达能力。",
      "published",
    ),
  }
  result = {}
  for key, (title, description, status) in course_specs.items():
    course = db.scalar(select(Course).where(Course.title == title))
    if course is None:
      course = Course(
        title=title,
        description=description,
        teacher_id=mentor.id,
        teacher_name=mentor.username,
        status=status,
      )
      db.add(course)
      db.flush()
    else:
      course.description = description
      course.teacher_id = mentor.id
      course.teacher_name = mentor.username
      course.status = status
    result[key] = course
  return result


def seed_chapters(db, courses):
  chapter_specs = {
    "space": [
      ("任务 1：星球分数补给站", "理解分数的意义，学会比较大小。"),
      ("任务 2：图形飞船设计局", "认识平面图形和对称，完成飞船设计。"),
      ("任务 3：逻辑迷宫挑战", "用表格和排除法解决趣味推理题。"),
    ],
    "science": [
      ("实验 1：瓶中彩虹", "观察密度差异，记录颜色分层。"),
      ("实验 2：磁力寻宝", "探索磁铁能吸引哪些材料。"),
      ("实验 3：会呼吸的叶子", "观察植物和空气泡泡。"),
    ],
    "reading": [
      ("绘本精读：月亮邮差", "抓住人物、地点和关键事件。"),
      ("表达训练：三句话讲故事", "练习清楚表达开头、经过、结果。"),
    ],
    "python": [
      ("第 1 课：让小海龟画星星", "认识指令和循环。"),
      ("第 2 课：我的互动问答机", "学习输入、判断和反馈。"),
    ],
  }
  result = {}
  for course_key, specs in chapter_specs.items():
    course = courses[course_key]
    result[course_key] = []
    for index, (title, description) in enumerate(specs, start=1):
      chapter = db.scalar(
        select(CourseChapter).where(CourseChapter.course_id == course.id, CourseChapter.sort_order == index)
      )
      if chapter is None:
        chapter = CourseChapter(course_id=course.id, title=title, description=description, sort_order=index)
        db.add(chapter)
        db.flush()
      else:
        chapter.title = title
        chapter.description = description
      result[course_key].append(chapter)
  return result


def seed_files(db, mentor: User, courses, chapters):
  specs = [
    (
      "space",
      0,
      "星际数学探险-任务卡.txt",
      "分数像一块被平均切开的星球能量饼。比较分数时，先看分母代表被分成几份，再看分子代表拿到几份。"
      "在星际补给任务中，同学们需要判断 3/4 和 2/3 哪一份能量更多，并说明理由。",
    ),
    (
      "science",
      0,
      "瓶中彩虹实验记录.txt",
      "把不同密度的液体慢慢倒入透明瓶子，会看到像彩虹一样的分层。记录时要写清材料、步骤、观察和猜想。"
      "如果液体混在一起，可能是倒入速度太快，或密度差异不够明显。",
    ),
    (
      "reading",
      0,
      "月亮邮差阅读单.txt",
      "阅读故事时，可以用人物、地点、事件、心情四个线索整理内容。复述时先讲谁在哪里，再讲发生了什么，最后讲变化。"
    ),
    (
      "python",
      0,
      "海龟画星星代码提示.txt",
      "使用 turtle.forward 和 turtle.right 可以控制小海龟移动。重复的动作可以放进 for 循环，让图形更整齐。"
    ),
  ]
  result = []
  ingestion = KnowledgeIngestionService(db)
  for course_key, chapter_index, original_name, content in specs:
    course = courses[course_key]
    chapter = chapters[course_key][chapter_index]
    stored_name = f"demo-{course_key}-{chapter_index + 1}.txt"
    path = UPLOAD_DIR / stored_name
    path.write_text(content, encoding="utf-8")
    file_asset = db.scalar(select(FileAsset).where(FileAsset.stored_name == stored_name))
    if file_asset is None:
      file_asset = FileAsset(
        original_name=original_name,
        stored_name=stored_name,
        content_type="text/plain",
        size=len(content.encode("utf-8")),
        course_id=course.id,
        chapter_id=chapter.id,
        storage_provider="local",
        object_key=stored_name,
        public_url=None,
        uploader_id=mentor.id,
        uploader_name=mentor.username,
      )
      db.add(file_asset)
      db.flush()
    else:
      file_asset.original_name = original_name
      file_asset.size = len(content.encode("utf-8"))
      file_asset.course_id = course.id
      file_asset.chapter_id = chapter.id
      file_asset.uploader_id = mentor.id
      file_asset.uploader_name = mentor.username
    ingestion.ingest_file(file_asset, content.encode("utf-8"))
    result.append(file_asset)
  return result


def seed_forum(db, users, courses):
  post_specs = [
    (
      "space",
      users["student"],
      "3/4 和 2/3 谁的星球能量更多？",
      "我画了两个一样大的能量饼，感觉 3/4 比 2/3 多。有没有更快的比较方法？\n\n我想到可以通分成 9/12 和 8/12。",
    ),
    (
      "science",
      users["star"],
      "瓶中彩虹为什么会分层？",
      "今天实验看到颜色一层一层叠起来，好像小彩虹。是不是因为每种液体的重量不一样？",
    ),
    (
      "reading",
      users["mentor"],
      "本周阅读打卡：用三句话讲清一个故事",
      "请同学们尝试用“谁在哪里、遇到了什么、最后有什么变化”三句话复述今天的绘本。",
    ),
    (
      "python",
      users["student"],
      "小海龟画星星总是歪掉怎么办？",
      "我用了 forward 和 right，但是最后一笔接不上。是不是角度应该固定？",
    ),
  ]
  posts = []
  for course_key, author, title, content in post_specs:
    course = courses[course_key]
    post = db.scalar(select(ForumPost).where(ForumPost.title == title))
    if post is None:
      post = ForumPost(
        title=title,
        content=content,
        attachments="[]",
        author_id=author.id,
        author_name=author.username,
        course_id=course.id,
        status="active",
      )
      db.add(post)
      db.flush()
    else:
      post.content = content
      post.author_id = author.id
      post.author_name = author.username
      post.course_id = course.id
      post.status = "active"
    posts.append(post)
  db.flush()

  comments = [
    (posts[0], users["mentor"], "你的通分思路很棒，也可以用交叉相乘快速比较：3×3 和 2×4。"),
    (posts[0], users["star"], "我画图也看出来 3/4 多一点，通分后更清楚。"),
    (posts[1], users["mentor"], "可以这样理解：密度不同会影响液体分层，倒入速度也很关键。"),
    (posts[3], users["mentor"], "五角星常用转角 144 度，可以先试试重复 5 次。"),
  ]
  for post, author, content in comments:
    existing = db.scalar(
      select(ForumComment).where(
        ForumComment.post_id == post.id,
        ForumComment.author_id == author.id,
        ForumComment.content == content,
      )
    )
    if existing is None:
      db.add(ForumComment(post_id=post.id, author_id=author.id, author_name=author.username, content=content))

  for post in posts:
    for user in (users["student"], users["mentor"], users["star"]):
      if post.author_id == user.id:
        continue
      like = db.scalar(select(ForumLike).where(ForumLike.post_id == post.id, ForumLike.user_id == user.id))
      if like is None:
        db.add(ForumLike(post_id=post.id, user_id=user.id))
  return posts


def seed_messages(db, users, posts):
  db.execute(delete(UserMessage).where(UserMessage.recipient_name.in_(["demo_student", "demo_mentor", "star_reader"])))
  messages = [
    UserMessage(
      recipient_id=users["student"].id,
      recipient_name=users["student"].username,
      sender_id=users["mentor"].id,
      sender_name=users["mentor"].username,
      message_type="announcement",
      title="今晚 8 点有星际数学直播答疑",
      content="准备好你的任务卡和问题，我们一起把分数补给站闯过去。",
      source_type="announcement",
      is_read=False,
    ),
    UserMessage(
      recipient_id=users["student"].id,
      recipient_name=users["student"].username,
      sender_id=users["star"].id,
      sender_name=users["star"].username,
      message_type="comment",
      title="你的帖子收到新评论",
      content="star_reader 评论了《3/4 和 2/3 谁的星球能量更多？》：通分后更清楚。",
      source_type="forum_post",
      source_id=posts[0].id,
      is_read=False,
    ),
    UserMessage(
      recipient_id=users["mentor"].id,
      recipient_name=users["mentor"].username,
      sender_id=users["student"].id,
      sender_name=users["student"].username,
      message_type="private",
      title="我完成了小海龟星星作品",
      content="老师，我已经把循环改好了，想请你帮我看看角度是不是正确。",
      source_type="private_message",
      is_read=False,
    ),
  ]
  db.add_all(messages)


def seed_assistant(db, student: User, course: Course):
  db.execute(delete(AssistantMessage).where(AssistantMessage.user_id == student.id))
  db.execute(delete(AssistantSession).where(AssistantSession.user_id == student.id))
  session = AssistantSession(user_id=student.id, course_id=course.id, title="分数比较怎么想")
  db.add(session)
  db.flush()
  citations = [
    {
      "document_id": "file:demo-space",
      "title": "星际数学探险-任务卡.txt",
      "chunk_index": 1,
      "snippet": "比较分数时，先看分母代表被分成几份，再看分子代表拿到几份。",
      "source_url": "/api/files/1/download",
    }
  ]
  db.add_all(
    [
      AssistantMessage(
        session_id=session.id,
        user_id=student.id,
        course_id=course.id,
        role="user",
        content="3/4 和 2/3 除了通分，还能怎么比较？",
        citations="[]",
      ),
      AssistantMessage(
        session_id=session.id,
        user_id=student.id,
        course_id=course.id,
        role="assistant",
        content="可以用交叉相乘：比较 3×3 和 2×4，9 大于 8，所以 3/4 更大。也可以画两个同样大的能量饼来验证。",
        citations=json.dumps(citations, ensure_ascii=False),
      ),
    ]
  )


def seed_learning_events(db, student: User, mentor: User, courses, files, posts):
  db.execute(delete(LearningEvent).where(LearningEvent.user_id.in_([student.id, mentor.id])))
  now = datetime.now(timezone.utc)
  events = [
    (student, courses["space"], "course_enrolled", {"course_title": courses["space"].title}, 9),
    (student, courses["science"], "course_enrolled", {"course_title": courses["science"].title}, 7),
    (student, courses["space"], "forum_post_created", {"post_title": posts[0].title}, 5),
    (student, courses["space"], "assistant_question", {"question": "分数比较有哪些方法？"}, 3),
    (student, courses["python"], "forum_post_created", {"post_title": posts[3].title}, 1),
    (mentor, courses["space"], "chapter_created", {"course_title": courses["space"].title, "chapter_title": "任务 1：星球分数补给站"}, 8),
    (mentor, courses["space"], "file_uploaded", {"file_name": files[0].original_name, "chunk_count": "1"}, 6),
    (mentor, courses["science"], "forum_comment_created", {"post_title": posts[1].title}, 2),
  ]
  for user, course, event_type, payload, days_ago in events:
    db.add(
      LearningEvent(
        user_id=user.id,
        course_id=course.id,
        event_type=event_type,
        event_payload=json.dumps(payload, ensure_ascii=False),
        created_at=now - timedelta(days=days_ago),
      )
    )

  for course in (courses["space"], courses["science"]):
    enrollment = db.scalar(
      select(CourseEnrollment).where(CourseEnrollment.course_id == course.id, CourseEnrollment.student_id == student.id)
    )
    if enrollment is None:
      db.add(CourseEnrollment(course_id=course.id, student_id=student.id, student_name=student.username))


if __name__ == "__main__":
  main()
