from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models import Todo, TodoCreate, TodoUpdate
from app.auth import get_current_user, get_user_id
from app.supabase_client import supabase_admin

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/")
def get_todos(
    user_id: str = Depends(get_user_id),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    response = (
        supabase_admin.table("todos")
        .select("*", count="exact")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {"data": response.data, "total": response.count, "limit": limit, "offset": offset}


@router.post("/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user)):
    response = (
        supabase_admin.table("todos")
        .insert({
            "user_id": current_user["sub"],
            "text": todo.text,
            "priority": todo.priority,
            "category": todo.category,
            "due_date": todo.due_date,
            "completed": False,
            "notes": todo.notes,
            "created_by_email": current_user["email"],
            "created_by_name": current_user["display_name"],
        })
        .execute()
    )
    return response.data[0]


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: str,
    updates: TodoUpdate,
    user_id: str = Depends(get_user_id),
):
    existing = (
        supabase_admin.table("todos")
        .select("id, user_id")
        .eq("id", todo_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own tasks")

    payload = updates.model_dump(exclude_none=True)
    response = (
        supabase_admin.table("todos")
        .update(payload)
        .eq("id", todo_id)
        .execute()
    )
    return response.data[0]


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str, user_id: str = Depends(get_user_id)):
    existing = (
        supabase_admin.table("todos")
        .select("id, user_id")
        .eq("id", todo_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own tasks")

    supabase_admin.table("todos").delete().eq("id", todo_id).execute()
