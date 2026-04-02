# Функции раздела “Подзадачи” в client.js

|Функция|	Описание|
|---|---|
|getSubtasks(taskId)|	Получить все подзадачи задачи<br>→ GET /api/tasks/{taskId}/subtasks
|updateSubtask(taskId, subtaskId, data)|	Обновить подзадачу<br>→ PUT /api/tasks/{taskId}/subtasks/{subtaskId}<br>Данные: { title?, due_date?, is_completed? }
|deleteSubtask(taskId, subtaskId)|	Удалить подзадачу<br>→ DELETE /api/tasks/{taskId}/subtasks/{subtaskId}
|createSubtask(taskId, data)|	Создать новую подзадачу<br>→ POST /api/tasks/{taskId}/subtasks<br>Данные: { title, due_date, is_completed } 
|getSubtaskByID(taskId, subtaskId)|	Получить подзадачу по ID<br>→ GET /api/tasks/{taskId}/subtasks/{subtaskId}
|updateSubtask(taskId, subtaskId, data)|	Обновить подзадачу<br>→ PUT /api/tasks/{taskId}/subtasks/{subtaskId}<br>Данные: { title?, due_date?, is_completed? }
|deleteSubtask(taskId, subtaskId)|	Удалить подзадачу<br>→ DELETE /api/tasks/{taskId}/subtasks/{subtaskId}
|getSubtasks(taskId)|	Получить все подзадачи задачи
|updateSubtask(taskId, subtaskId, data)|	Обновить подзадачу
|deleteSubtask(taskId, subtaskId)|	Удалить подзадачу
|getSubtaskByID(taskId, subtaskId)|	Получить подзадачу по ID
|createSubtask(taskId, data)|	Создать новую подзадачу|
|updateSubtask(taskId, subtaskId, data)|	Обновить подзадачу|
|deleteSubtask(taskId, subtaskId)|	Удалить подзадачу|
getSubtasks(taskId)	Получить все подзадачи задачиsubtasks
createSubtask(taskId, data)	Создать новую подзадачу<br>→ POST /api/tasks/{taskId}/subtasks<br>Данные: { title, due_date, is_completed }
updateSubtask(taskId, subtaskId, data)	Обновить подзадачу<br>→ PUT /api/tasks/{taskId}/subtasks/{subtaskId}<br>Данные: { title?, due_date?, is_completed? }
deleteSubtask(taskId, subtaskId)	Удалить подзадачу<br>→ DELETE /api/tasks/{taskId}/subtasks/{subtaskId}
