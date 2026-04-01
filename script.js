const API_BASE_URL = "http://127.0.0.1:5000";

const endpoints = {
  games: `${API_BASE_URL}/games`
};

const gamesTableBody = document.getElementById("gamesTableBody");
const messageBox = document.getElementById("messageBox");
const formCard = document.getElementById("formCard");
const formTitle = document.getElementById("formTitle");
const gameForm = document.getElementById("gameForm");
const submitBtn = document.getElementById("submitBtn");
const showAddFormBtn = document.getElementById("showAddFormBtn");
const cancelBtn = document.getElementById("cancelBtn");
const refreshBtn = document.getElementById("refreshBtn");
const searchInput = document.getElementById("searchInput");

let isEditMode = false;
let editingGameId = null;
let allGames = [];

function showMessage(text, type = "success") {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
}

function clearMessage() {
  messageBox.textContent = "";
  messageBox.className = "message";
}

function showForm() {
  formCard.classList.add("active");
}

function hideForm() {
  formCard.classList.remove("active");
}

function resetForm() {
  gameForm.reset();
  document.getElementById("id").disabled = false;
  isEditMode = false;
  editingGameId = null;
  formTitle.textContent = "Add Game";
  submitBtn.textContent = "Save Game";
}

function populateForm(game) {
  document.getElementById("id").value = game.id ?? "";
  document.getElementById("name").value = game.name ?? "";
  document.getElementById("genre").value = game.genre ?? "";
  document.getElementById("year_released").value = game.year_released ?? "";
  document.getElementById("developer").value = game.developer ?? "";
  document.getElementById("platforms").value = game.platforms ?? "";
}

function getFormData() {
  return {
    id: Number(document.getElementById("id").value),
    name: document.getElementById("name").value.trim(),
    genre: document.getElementById("genre").value.trim(),
    year_released: Number(document.getElementById("year_released").value),
    developer: document.getElementById("developer").value.trim(),
    platforms: document.getElementById("platforms").value.trim()
  };
}

function validateGameData(game) {
  if (!Number.isInteger(game.id)) {
    return "ID must be an integer.";
  }

  if (!game.name) {
    return "Name is required.";
  }

  if (!game.genre) {
    return "Genre is required.";
  }

  if (!Number.isInteger(game.year_released)) {
    return "Year Released must be an integer.";
  }

  if (!game.developer) {
    return "Developer is required.";
  }

  if (!game.platforms) {
    return "Platforms is required.";
  }

  return null;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderGames(games) {
  if (!Array.isArray(games) || games.length === 0) {
    const searchText = searchInput.value.trim();

    gamesTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">
          ${searchText ? "No matching games found." : "No games found."}
        </td>
      </tr>
    `;
    return;
  }

  gamesTableBody.innerHTML = games
    .map((game) => {
      const safeId = escapeHtml(String(game.id ?? ""));
      const safeName = escapeHtml(String(game.name ?? ""));
      const safeGenre = escapeHtml(String(game.genre ?? ""));
      const safeYear = escapeHtml(String(game.year_released ?? ""));
      const safeDeveloper = escapeHtml(String(game.developer ?? ""));
      const safePlatforms = escapeHtml(String(game.platforms ?? ""));

      return `
        <tr>
          <td>${safeId}</td>
          <td>${safeName}</td>
          <td>${safeGenre}</td>
          <td>${safeYear}</td>
          <td>${safeDeveloper}</td>
          <td>${safePlatforms}</td>
          <td class="actions-cell">
            <button class="btn-edit" onclick="startEdit(${Number(game.id)})">Update</button>
            <button class="btn-delete" onclick="deleteGame(${Number(game.id)})">Delete</button>
          </td>
        </tr>
      `;
    })
    .join("");
}

function filterGames(searchTerm) {
  const normalizedSearch = searchTerm.trim().toLowerCase();

  if (!normalizedSearch) {
    renderGames(allGames);
    return;
  }

  const filteredGames = allGames.filter((game) => {
    return [
      String(game.id ?? ""),
      String(game.name ?? ""),
      String(game.genre ?? ""),
      String(game.year_released ?? ""),
      String(game.developer ?? ""),
      String(game.platforms ?? "")
    ].some((field) => field.toLowerCase().includes(normalizedSearch));
  });

  renderGames(filteredGames);
}

async function fetchGames() {
  clearMessage();

  gamesTableBody.innerHTML = `
    <tr>
      <td colspan="7" class="empty-state">Loading games...</td>
    </tr>
  `;

  try {
    const response = await fetch(endpoints.games, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch games. Status: ${response.status}`);
    }

    const games = await response.json();
    allGames = Array.isArray(games) ? games : [];
    filterGames(searchInput.value);
  } catch (error) {
    console.error("Error fetching games:", error);

    gamesTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">Could not load games.</td>
      </tr>
    `;

    showMessage(`Error loading games: ${error.message}`, "error");
  }
}

async function createGame(game) {
  const response = await fetch(endpoints.games, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(game)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Create failed (${response.status}): ${errorText}`);
  }

  return response;
}

async function updateGame(id, game) {
  const response = await fetch(`${endpoints.games}/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(game)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Update failed (${response.status}): ${errorText}`);
  }

  return response;
}

async function deleteGame(id) {
  const confirmed = window.confirm(`Are you sure you want to delete game with ID ${id}?`);

  if (!confirmed) {
    return;
  }

  clearMessage();

  try {
    const response = await fetch(`${endpoints.games}/${id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Delete failed (${response.status}): ${errorText}`);
    }

    showMessage(`Game with ID ${id} deleted successfully.`, "success");
    await fetchGames();
  } catch (error) {
    console.error("Error deleting game:", error);
    showMessage(`Error deleting game: ${error.message}`, "error");
  }
}

async function startEdit(id) {
  clearMessage();

  try {
    const game = allGames.find((item) => Number(item.id) === Number(id));

    if (!game) {
      throw new Error(`Game with ID ${id} not found.`);
    }

    isEditMode = true;
    editingGameId = Number(id);

    formTitle.textContent = "Update Game";
    submitBtn.textContent = "Update Game";
    showForm();
    populateForm(game);

    document.getElementById("id").disabled = true;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    console.error("Error starting edit:", error);
    showMessage(`Error preparing update: ${error.message}`, "error");
  }
}

gameForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();

  const game = getFormData();
  const validationError = validateGameData(game);

  if (validationError) {
    showMessage(validationError, "error");
    return;
  }

  try {
    if (isEditMode) {
      const payload = {
        id: editingGameId,
        name: game.name,
        genre: game.genre,
        year_released: game.year_released,
        developer: game.developer,
        platforms: game.platforms
      };

      await updateGame(editingGameId, payload);
      showMessage(`Game with ID ${editingGameId} updated successfully.`, "success");
    } else {
      await createGame(game);
      showMessage(`Game with ID ${game.id} created successfully.`, "success");
    }

    resetForm();
    hideForm();
    await fetchGames();
  } catch (error) {
    console.error("Form submission error:", error);
    showMessage(error.message, "error");
  }
});

showAddFormBtn.addEventListener("click", () => {
  clearMessage();
  resetForm();
  showForm();
});

cancelBtn.addEventListener("click", () => {
  clearMessage();
  resetForm();
  hideForm();
});

refreshBtn.addEventListener("click", async () => {
  await fetchGames();
});

searchInput.addEventListener("input", (event) => {
  filterGames(event.target.value);
});

window.startEdit = startEdit;
window.deleteGame = deleteGame;

fetchGames();