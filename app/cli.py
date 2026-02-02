import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User, Todo, Category
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        
        bob = User(username='bob', email='bob@mail.com') # Create a new user (in memory)
        bob.set_password("bobpass")

        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)

        new_todo = Todo(text='Wash dishes', user_id=bob.id)

        db.add(new_todo) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(new_todo) # Update the user (we use this to get the ID from the db)

        print("Database Initialized")


    # Task 4.1 code here. Remove the line with "pass" below once completed
@cli.command()
def add_task(username:str, task:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        user.todos.append(Todo(text=task))
        db.add(user)
        db.commit()
        print("Task added for user")
    #pass

@cli.command()
def toggle_todo(todo_id:int, username:str):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("This todo doesn't exist")
            return
        if todo.user.username != username:
            print(f"This todo doesn't belong to {username}")
            return

        todo.toggle()
        db.add(todo)
        db.commit()

        print(f"Todo item's done state set to {todo.done}")
    # Task 4.2 code here. Remove the line with "pass" below once completed
   # pass


@cli.command()
def list_todo_categories(todo_id:int, username:str):
    with get_session() as db: # Get a connection to the database
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
        elif not todo.user.username == username:
            print("Todo doesn't belong to that user")
        else:
            print(f"Categories: {todo.categories}")
    # Task 5.3 code here. Remove the line with "pass" below once completed
  #  pass

   
@cli.command()
def create_category(username:str, cat_text:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return

        category = db.exec(select(Category).where(Category.text== cat_text, Category.user_id == user.id)).one_or_none()
        if category:
            print("Category exists! Skipping creation")
            return
        
        category = Category(text=cat_text, user_id=user.id)
        db.add(category)
        db.commit()

        print("Category added for user")    
    # Task 5.4 code here. Remove the line with "pass" below once completed
   # pass

@cli.command()
def list_user_categories(username:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        categories = db.exec(select(Category).where(Category.user_id == user.id)).all()
        print([category.text for category in categories])
    # Task 5.5 code here. Remove the line with "pass" below once completed
   # pass


@cli.command()
def assign_category_to_todo(username:str, todo_id:int, category_text:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        
        category = db.exec(select(Category).where(Category.text == category_text, Category.user_id==user.id)).one_or_none()
        if not category:
            category = Category(text=category_text, user_id=user.id)
            db.add(category)
            db.commit()
            print("Category didn't exist for user, creating it")
        
        todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id==user.id)).one_or_none()
        if not todo:
            print("Todo doesn't exist for user")
            return
        
        todo.categories.append(category)
        db.add(todo)
        db.commit()
        print("Added category to todo")
    # Task 5.6 code here. Remove the line with "pass" below once completed
  #  pass
#11. Conclusion
#Thus concludes your introduction to flask-sqlalchemy. The usage of this library is at the very core of this course.

#You can view a completed version of this lab at the following link


##exercises 
@cli.command()
def see_todo():
     with get_session() as db:
         todoslist = db.exec(select(Todo)).all()
         print([todoeach.id for todoeach in todoslist])
         print([todoeach.user_id for todoeach in todoslist])
         print([todoeach.text for todoeach in todoslist])
         print([todoeach.done for todoeach in todoslist])
         print([(todoeach.id, todoeach.user_id, todoeach.text, todoeach.done) for todoeach in todoslist])

@cli.command()
def delete_todo(todo_id: int):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
        else:
            print("Deleting todo {todo_id}")
            db.delete(todo)
            db.commit()

@cli.command()
def mark_all_done(userid: int):
    with get_session() as db:
        
        todo = db.exec(select(Todo).where(Todo.user_id == userid))
        for one in todo:
            one.toggle()
            db.add(one)
            db.commit()

            
        


if __name__ == "__main__":
    cli()
