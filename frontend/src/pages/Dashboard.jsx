// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import {
  createTask,
  deleteTask,
  getTasks,
  ping,
  toggleTask,
  updateTask,
} from "../api/api";
import useAuth from "../hooks/useAuth";

const EMPTY_FORM = { title: "", description: "", due_date: "", priority: "medium" };

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [apiStatus, setApiStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [filter, setFilter] = useState("all");
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState(EMPTY_FORM);

  useEffect(() => {
    const load = async () => {
      try {
        const [pingRes, taskList] = await Promise.all([ping(), getTasks()]);
        setApiStatus(pingRes);
        setTasks(taskList);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
        setError("Could not load your tasks. Is the backend running?");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setError("");
    try {
      const created = await createTask({
        ...form,
        due_date: form.due_date || null,
      });
      setTasks((prev) => [created, ...prev]);
      setForm(EMPTY_FORM);
    } catch (err) {
      console.error("Failed to create task:", err);
      setError("Could not create the task. Please try again.");
    }
  };

  const handleToggle = async (id) => {
    try {
      const updated = await toggleTask(id);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      console.error("Failed to toggle task:", err);
      setError("Could not update the task. Please try again.");
    }
  };

  const startEditing = (task) => {
    setEditingId(task.id);
    setEditForm({
      title: task.title,
      description: task.description || "",
      due_date: task.due_date || "",
      priority: task.priority,
    });
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editForm.title.trim()) return;
    try {
      const updated = await updateTask(editingId, {
        ...editForm,
        due_date: editForm.due_date || null,
      });
      setTasks((prev) => prev.map((t) => (t.id === editingId ? updated : t)));
      setEditingId(null);
    } catch (err) {
      console.error("Failed to save task:", err);
      setError("Could not save the task. Please try again.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this task?")) return;
    try {
      await deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error("Failed to delete task:", err);
      setError("Could not delete the task. Please try again.");
    }
  };

  const visibleTasks = tasks.filter((t) => {
    if (filter === "active") return !t.completed;
    if (filter === "completed") return t.completed;
    return true;
  });
  const remaining = tasks.filter((t) => !t.completed).length;

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1>My Tasks</h1>
          {user && <p className="dashboard__welcome">Welcome back, {user.username}</p>}
          {apiStatus && <p className="dashboard__status">API: {apiStatus.ping}</p>}
        </div>
        <button className="btn btn--secondary" onClick={logout}>Logout</button>
      </header>

      {error && <p className="dashboard__error">{error}</p>}

      <form className="task-form" onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="What needs doing?"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <input
          type="date"
          value={form.due_date}
          onChange={(e) => setForm({ ...form, due_date: e.target.value })}
          aria-label="Due date"
        />
        <select
          value={form.priority}
          onChange={(e) => setForm({ ...form, priority: e.target.value })}
          aria-label="Priority"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button className="btn btn--primary" type="submit">Add Task</button>
      </form>

      <div className="task-filters">
        {["all", "active", "completed"].map((f) => (
          <button
            key={f}
            className={filter === f ? "btn btn--primary" : "btn btn--secondary"}
            onClick={() => setFilter(f)}
          >
            {f[0].toUpperCase() + f.slice(1)}
            {f === "all" && ` (${tasks.length})`}
            {f === "active" && ` (${remaining})`}
            {f === "completed" && ` (${tasks.length - remaining})`}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading tasks…</p>
      ) : visibleTasks.length === 0 ? (
        <p className="task-empty">
          {tasks.length === 0
            ? "No tasks yet — add your first one above."
            : "Nothing here. Try a different filter."}
        </p>
      ) : (
        <ul className="task-list">
          {visibleTasks.map((task) => (
            <li key={task.id} className={`task-item${task.completed ? " task-item--done" : ""}`}>
              {editingId === task.id ? (
                <form className="task-form task-form--edit" onSubmit={handleSaveEdit}>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Description (optional)"
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  />
                  <input
                    type="date"
                    value={editForm.due_date}
                    onChange={(e) => setEditForm({ ...editForm, due_date: e.target.value })}
                    aria-label="Due date"
                  />
                  <select
                    value={editForm.priority}
                    onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                    aria-label="Priority"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                  <button className="btn btn--primary" type="submit">Save</button>
                  <button
                    className="btn btn--secondary"
                    type="button"
                    onClick={() => setEditingId(null)}
                  >
                    Cancel
                  </button>
                </form>
              ) : (
                <>
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggle(task.id)}
                    aria-label={`Mark "${task.title}" ${task.completed ? "incomplete" : "complete"}`}
                  />
                  <div className="task-item__body">
                    <span className="task-item__title">{task.title}</span>
                    {task.description && (
                      <span className="task-item__description">{task.description}</span>
                    )}
                    <span className="task-item__meta">
                      <span className={`task-item__priority task-item__priority--${task.priority}`}>
                        {task.priority}
                      </span>
                      {task.due_date && <span>Due {task.due_date}</span>}
                    </span>
                  </div>
                  <button className="btn btn--secondary" onClick={() => startEditing(task)}>
                    Edit
                  </button>
                  <button className="btn btn--danger" onClick={() => handleDelete(task.id)}>
                    Delete
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
