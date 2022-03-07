from fastapi import Depends, Response, status, HTTPException, APIRouter
from .. import models, schema
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import oauth2
from typing import Optional

router = APIRouter(prefix="/posts", tags=["Posts"])

my_posts = [
    {"title": "Title Post 1", "content": "Content of Post 1", "id": 1},
    {"title": "Title Post 2", "content": "Content of Post 2", "id": 2},
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@router.get("/")
def get_posts(
    db: Session = Depends(get_db),
    response_model=schema.PostOut,
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    print(limit)
    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id)
        .group_by(models.Post.id)
        # .all()
    )

    print(results)
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_posts(
    post: schema.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """,
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    return new_post


@router.get("/latest")
def get_latest_post(current_user: int = Depends(oauth2.get_current_user)):
    post = my_posts[len(my_posts) - 1]
    return post


@router.get("/{id}")
def get_post(
    id: int,
    response: Response,
    db: Session = Depends(get_db),
    response_model=schema.Post,
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # cursor.execute(sql.SQL("SELECT * FROM posts WHERE id = %s"), [str(id)])
    # post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={id} was not found",
        )
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_q = db.query(models.Post).filter(models.Post.id == id)
    # cursor.execute(sql.SQL("DELETE FROM posts WHERE id = %s RETURNING *"), [str(id)])
    # deleted_post = cursor.fetchone()
    if post_q.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID={id} does not exist",
        )
    # conn.commit()

    if post_q.first().owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to preform delete on this post",
        )

    post_q.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(
    id: int,
    post: schema.PostCreate,
    db: Session = Depends(get_db),
    response_model=schema.Post,
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     sql.SQL(
    #         "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"
    #     ),
    #     [post.title, post.content, post.published, str(id)],
    # )
    # updated_post = cursor.fetchone()

    post_q = db.query(models.Post).filter(models.Post.id == id)
    post_updated = post_q.first()

    if post_updated == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID={id} does not exist",
        )
    if post_updated.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to preform delete on this post",
        )
    # conn.commit()
    post_q.update(
        post.dict(),
        synchronize_session=False,
    )
    db.commit()
    return post_q.first()
