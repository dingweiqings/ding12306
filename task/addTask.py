from task.cerely import app
@app.task
def add(x, y):
    return addSub(x,y)
def addSub(x,y):
    print("Add sub")
    return x+y
