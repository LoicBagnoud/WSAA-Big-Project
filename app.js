// This is the Javascript functions that allow the page to behave the way it does
// Author: ChatGPT - Reference below

const API_BASE_URL = "";
const GAMES_URL = `${API_BASE_URL}/games`;
const DEFAULT_BOX_ART = "images/not-found.png";
const MIN_YEAR = 1950;
const MAX_YEAR = new Date().getFullYear();

let allGames = [];
let isEditMode = false;
let editingGameId = null;
let currentSearchTerm = "";

const $gamesTableBody = $("#gamesTableBody");
const $messageBox = $("#messageBox");
const $formCard = $("#formCard");
const $formTitle = $("#formTitle");
const $gameForm = $("#gameForm");
const $submitBtn = $("#submitBtn");
const $showAddFormBtn = $("#showAddFormBtn");
const $cancelBtn = $("#cancelBtn");
const $refreshBtn = $("#refreshBtn");
const $searchInput = $("#searchInput");
const $yearReleasedInput = $("#year_released");

function showMessage(text, type = "success") {
  $messageBox.text(text).removeClass("success error").addClass(type);
}

function clearMessage() {
  $messageBox.text("").removeClass("success error");
}

function showForm() {
  $formCard.addClass("active");
}

function hideForm() {
  $formCard.removeClass("active");
}

function populateYearDropdown() {
  $yearReleasedInput.empty();
  $yearReleasedInput.append('<option value="">Select a year</option>');

  for (let year = MAX_YEAR; year >= MIN_YEAR; year -= 1) {
    $yearReleasedInput.append(`<option value="${year}">${year}</option>`);
  }
}

function resetForm() {
  $gameForm[0].reset();
  isEditMode = false;
  editingGameId = null;
  $formTitle.text("Add Game");
  $submitBtn.text("Save Game");
  $yearReleasedInput.val("");
}

function populateForm(game) {
  $("#name").val(game.name ?? "");
  $("#genre").val(game.genre ?? "");
  $("#year_released").val(String(game.year_released ?? ""));
  $("#developer").val(game.developer ?? "");
  $("#platforms").val(game.platforms ?? "");
}

function getFormData() {
  return {
    name: $("#name").val().trim(),
    genre: $("#genre").val().trim(),
    year_released: Number($("#year_released").val()),
    developer: $("#developer").val().trim(),
    platforms: $("#platforms").val().trim()
  };
}

function validateGameData(game) {
  if (!game.name) {
    return "Name is required.";
  }

  if (!game.genre) {
    return "Genre is required.";
  }

  if (!Number.isInteger(game.year_released) || game.year_released < MIN_YEAR || game.year_released > MAX_YEAR) {
    return `Year Released must be between ${MIN_YEAR} and ${MAX_YEAR}.`;
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
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function gameMatchesSearch(game, normalizedSearch) {
  return String(game.name ?? "").toLowerCase().startsWith(normalizedSearch);
}

function renderEmptyState(message) {
  $gamesTableBody.html(`
    <tr>
      <td colspan="7" class="empty-state">${message}</td>
    </tr>
  `);
}

function getBoxArtUrl(game) {
  const rawUrl = String(game.boxcover_url ?? "").trim();
  return rawUrl ? rawUrl : DEFAULT_BOX_ART;
}

function renderGames(games) {
  if (!Array.isArray(games) || games.length === 0) {
    renderEmptyState("No games found.");
    return;
  }

  const rowsHtml = games.map((game) => {
    const imageSrc = getBoxArtUrl(game);

    return `
      <tr class="game-row fading-in" data-id="${Number(game.id)}">
        <td class="name-cell">${escapeHtml(game.name ?? "")}</td>
        <td>${escapeHtml(game.genre ?? "")}</td>
        <td>${escapeHtml(game.year_released ?? "")}</td>
        <td>${escapeHtml(game.developer ?? "")}</td>
        <td>${escapeHtml(game.platforms ?? "")}</td>
        <td class="box-art-cell">
          <img
            class="box-art-image"
            src="${escapeHtml(imageSrc)}"
            alt="${escapeHtml(game.name ?? "Game")} box cover"
            onerror="this.onerror=null; this.src='images/not-found.png';"
          />
          ${game.warning ? `<div class="box-art-warning">Image not found</div>` : ""}
        </td>
        <td class="actions-cell">
          <button class="btn-edit" onclick="startEdit(${Number(game.id)})">Update</button>
          <button class="btn-delete" onclick="deleteGame(${Number(game.id)})">Delete</button>
        </td>
      </tr>
    `;
  }).join("");

  $gamesTableBody.html(rowsHtml);
}

function applyFilter(searchTerm) {
  currentSearchTerm = searchTerm.trim().toLowerCase();

  if (!allGames.length) {
    renderEmptyState("No games found.");
    return;
  }

  const filteredGames = currentSearchTerm
    ? allGames.filter((game) => gameMatchesSearch(game, currentSearchTerm))
    : allGames;

  const visibleIds = new Set(filteredGames.map((game) => Number(game.id)));
  const $rows = $gamesTableBody.find("tr.game-row");

  if (!currentSearchTerm) {
    if ($rows.length !== allGames.length) {
      renderGames(allGames);
      return;
    }

    $rows.show().removeClass("fading-out").addClass("fading-in");
    return;
  }

  if (filteredGames.length === 0) {
    $rows.addClass("fading-out");

    setTimeout(() => {
      renderEmptyState("No matching games found.");
    }, 300);
    return;
  }

  if ($rows.length === 0 || $rows.length !== allGames.length) {
    renderGames(allGames);
  }

  const $allRows = $gamesTableBody.find("tr.game-row");

  $allRows.each(function () {
    const $row = $(this);
    const rowId = Number($row.data("id"));
    const isVisible = visibleIds.has(rowId);

    if (isVisible) {
      $row.stop(true, true).show();
      $row.removeClass("fading-out").addClass("fading-in");
    } else {
      $row.removeClass("fading-in").addClass("fading-out");

      setTimeout(() => {
        if (!visibleIds.has(rowId) && currentSearchTerm === searchTerm.trim().toLowerCase()) {
          $row.hide();
        }
      }, 300);
    }
  });
}

function fetchGames() {
  clearMessage();

  $gamesTableBody.html(`
    <tr>
      <td colspan="7" class="empty-state">Loading games...</td>
    </tr>
  `);

  $.ajax({
    url: GAMES_URL,
    method: "GET",
    dataType: "json",
    success: function (games) {
      allGames = Array.isArray(games) ? games : [];
      renderGames(allGames);
      applyFilter($searchInput.val());
    },
    error: function (xhr, status, error) {
      console.error("Error fetching games:", status, error, xhr.responseText);
      renderEmptyState("Could not load games.");
      showMessage("Error loading games.", "error");
    }
  });
}

function rollbackCreatedGame(createdGameId) {
  $.ajax({
    url: `${GAMES_URL}/${createdGameId}`,
    method: "DELETE",
    success: function () {
      showMessage("Game creation cancelled because no image was found.", "error");
      resetForm();
      hideForm();
      fetchGames();
    },
    error: function (xhr, status, error) {
      console.error("Rollback delete error:", status, error, xhr.responseText);
      showMessage(
        "Game was created, but automatic removal after warning failed.",
        "error"
      );
      resetForm();
      hideForm();
      fetchGames();
    }
  });
}

function createGame(game) {
  $.ajax({
    url: GAMES_URL,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(game),
    dataType: "json",
    success: function (createdGame) {
      if (createdGame.warning) {
        const keepEntry = window.confirm(
          `${createdGame.warning}\n\nDo you want to keep this game entry?`
        );

        if (!keepEntry) {
          rollbackCreatedGame(createdGame.id);
          return;
        }

        showMessage(createdGame.warning, "error");
      } else {
        showMessage("Game created successfully.", "success");
      }

      resetForm();
      hideForm();
      fetchGames();
    },
    error: function (xhr, status, error) {
      console.error("Create error:", status, error, xhr.responseText);
      const message =
        xhr.responseJSON?.message ||
        xhr.responseText ||
        "Failed to create game.";
      showMessage(message, "error");
    }
  });
}

function updateGame(id, game) {
  $.ajax({
    url: `${GAMES_URL}/${id}`,
    method: "PUT",
    contentType: "application/json",
    data: JSON.stringify(game),
    dataType: "json",
    success: function (updatedGame) {
      if (updatedGame.warning) {
        const keepChanges = window.confirm(
          `${updatedGame.warning}\n\nDo you want to keep these changes?`
        );

        if (!keepChanges) {
          showMessage(
            "Update saved, but you should correct the game title and update it again.",
            "error"
          );
          fetchGames();
          return;
        }

        showMessage(updatedGame.warning, "error");
      } else {
        showMessage("Game updated successfully.", "success");
      }

      resetForm();
      hideForm();
      fetchGames();
    },
    error: function (xhr, status, error) {
      console.error("Update error:", status, error, xhr.responseText);
      const message =
        xhr.responseJSON?.message ||
        xhr.responseText ||
        "Failed to update game.";
      showMessage(message, "error");
    }
  });
}

function deleteGame(id) {
  const confirmed = window.confirm("Are you sure you want to delete this game?");

  if (!confirmed) {
    return;
  }

  clearMessage();

  $.ajax({
    url: `${GAMES_URL}/${id}`,
    method: "DELETE",
    success: function () {
      showMessage("Game deleted successfully.", "success");
      fetchGames();
    },
    error: function (xhr, status, error) {
      console.error("Delete error:", status, error, xhr.responseText);
      const message =
        xhr.responseJSON?.message ||
        xhr.responseText ||
        "Failed to delete game.";
      showMessage(message, "error");
    }
  });
}

function startEdit(id) {
  clearMessage();

  $.ajax({
    url: `${GAMES_URL}/${id}`,
    method: "GET",
    dataType: "json",
    success: function (game) {
      isEditMode = true;
      editingGameId = Number(id);
      $formTitle.text("Update Game");
      $submitBtn.text("Update Game");
      populateForm(game);
      showForm();
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    error: function (xhr, status, error) {
      console.error("Edit load error:", status, error, xhr.responseText);
      const message =
        xhr.responseJSON?.message ||
        xhr.responseText ||
        "Could not load game for editing.";
      showMessage(message, "error");
    }
  });
}

$gameForm.on("submit", function (event) {
  event.preventDefault();
  clearMessage();

  const game = getFormData();
  const validationError = validateGameData(game);

  if (validationError) {
    showMessage(validationError, "error");
    return;
  }

  if (isEditMode) {
    updateGame(editingGameId, game);
  } else {
    createGame(game);
  }
});

$showAddFormBtn.on("click", function () {
  clearMessage();
  resetForm();
  showForm();
});

$cancelBtn.on("click", function () {
  clearMessage();
  resetForm();
  hideForm();
});

$refreshBtn.on("click", function () {
  fetchGames();
});

$searchInput.on("input", function () {
  applyFilter($(this).val());
});

window.startEdit = startEdit;
window.deleteGame = deleteGame;

$(document).ready(function () {
  populateYearDropdown();
  fetchGames();
});

// References:
// ChatGPT - https://chatgpt.com/share/69cfc0bc-c5ec-8384-9482-04af249039a8