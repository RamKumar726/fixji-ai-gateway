(() => {
  "use strict";

  const script = document.currentScript;
  const config = window.FixjiChatConfig || {};
  const apiBaseUrl = (
    config.apiBaseUrl ||
    script?.dataset.apiBase ||
    ""
  ).replace(/\/+$/, "");

  const host = document.createElement("div");
  host.id = "fixji-chat-widget";
  document.body.appendChild(host);

  const shadow = host.attachShadow({ mode: "open" });

  shadow.innerHTML = `
    <style>
      :host {
        all: initial;
        font-family: Arial, Helvetica, sans-serif;
        color: #17231e;
      }

      * {
        box-sizing: border-box;
      }

      button, textarea {
        font: inherit;
      }

      .launcher {
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 2147483000;
        width: 60px;
        height: 60px;
        border: 0;
        border-radius: 50%;
        background: #14834c;
        color: #fff;
        box-shadow: 0 8px 26px rgb(20 131 76 / 30%);
        cursor: pointer;
        font-size: 25px;
      }

      .panel {
        position: fixed;
        right: 24px;
        bottom: 96px;
        z-index: 2147483000;
        display: flex;
        width: min(380px, calc(100vw - 28px));
        height: min(580px, calc(100vh - 120px));
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #dfe8e1;
        border-radius: 16px;
        background: #fff;
        box-shadow: 0 16px 55px rgb(0 0 0 / 18%);
      }

      .panel[hidden] {
        display: none;
      }

      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 16px;
        background: #147c48;
        color: white;
      }

      .title {
        font-size: 15px;
        font-weight: 700;
      }

      .subtitle {
        margin-top: 4px;
        color: #d3efde;
        font-size: 12px;
      }

      .close {
        width: 34px;
        height: 34px;
        border: 0;
        border-radius: 8px;
        background: transparent;
        color: white;
        cursor: pointer;
        font-size: 22px;
      }

      .messages {
        display: flex;
        flex: 1;
        flex-direction: column;
        gap: 10px;
        overflow-y: auto;
        padding: 16px;
        background: #fbfdfb;
      }

      .message {
        max-width: 90%;
        padding: 10px 12px;
        border: 1px solid #e5ebe6;
        border-radius: 13px;
        background: white;
        font-size: 14px;
        line-height: 1.5;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
      }

      .message.user {
        align-self: flex-end;
        border-color: #d5efdf;
        background: #e7f6ec;
      }

      .message.error {
        max-width: 100%;
        border-color: #efcaca;
        background: #fff2f2;
        color: #922;
      }

      .message.pending {
        color: #68756c;
        font-style: italic;
      }

      .approval {
        padding: 12px;
        border: 1px solid #ecd7a8;
        border-radius: 12px;
        background: #fffaf0;
        font-size: 13px;
      }

      .approval-title {
        margin-bottom: 8px;
        font-weight: 700;
      }

      .approval-details {
        margin: 0;
        color: #5f5541;
        font: inherit;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
      }

      .approval-actions {
        display: flex;
        gap: 8px;
        margin-top: 10px;
      }

      .approval-actions button,
      .send {
        padding: 9px 12px;
        border: 0;
        border-radius: 9px;
        background: #14834c;
        color: white;
        cursor: pointer;
        font-weight: 700;
      }

      .approval-actions .reject {
        border: 1px solid #d9e1da;
        background: white;
        color: #45554b;
      }

      .composer {
        display: flex;
        align-items: end;
        gap: 8px;
        padding: 12px;
        border-top: 1px solid #edf1ee;
        background: white;
      }

      .input {
        min-width: 0;
        min-height: 42px;
        max-height: 100px;
        flex: 1;
        resize: vertical;
        padding: 10px;
        border: 1px solid #dce5de;
        border-radius: 9px;
        color: #17231e;
        font-size: 14px;
      }

      .send {
        min-height: 42px;
      }

      button:disabled,
      textarea:disabled {
        cursor: not-allowed;
        opacity: .6;
      }

      @media (max-width: 520px) {
        .launcher {
          right: 16px;
          bottom: 16px;
        }

        .panel {
          right: 10px;
          bottom: 84px;
          height: min(620px, calc(100vh - 100px));
        }
      }
    </style>

    <button class="launcher" type="button" aria-label="Open Fixji chat">✦</button>

    <section class="panel" role="dialog" aria-label="Fixji assistant" hidden>
      <header class="header">
        <div>
          <div class="title">Fixji Assistant</div>
          <div class="subtitle">How can we help?</div>
        </div>
        <button class="close" type="button" aria-label="Close chat">×</button>
      </header>

      <div class="messages" role="log" aria-live="polite"></div>

      <form class="composer">
        <textarea
          class="input"
          rows="1"
          maxlength="4000"
          aria-label="Your message"
          placeholder="Type your message..."
          required
        ></textarea>
        <button class="send" type="submit">Send</button>
      </form>
    </section>
  `;

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const closeButton = shadow.querySelector(".close");
  const messages = shadow.querySelector(".messages");
  const form = shadow.querySelector(".composer");
  const input = shadow.querySelector(".input");
  const sendButton = shadow.querySelector(".send");

  let sessionId = null;
  let busy = false;
  let awaitingApproval = false;

  function addMessage(text, kind = "") {
    const element = document.createElement("div");
    element.className = `message ${kind}`.trim();
    element.textContent = text;
    messages.appendChild(element);
    messages.scrollTop = messages.scrollHeight;
    return element;
  }

  function setBusy(value) {
    busy = value;
    input.disabled = value || awaitingApproval;
    sendButton.disabled = value || awaitingApproval;
  }

  async function getAccessToken() {
    if (typeof config.getAccessToken !== "function") {
      throw new Error(
        "Chat is not connected to Fixji login. Configure FixjiChatConfig.getAccessToken."
      );
    }

    const token = await config.getAccessToken();

    if (typeof token !== "string" || !token.trim()) {
      throw new Error("Please sign in to Fixji before using chat.");
    }

    return token;
  }

  async function apiRequest(path, body) {
    if (!apiBaseUrl) {
      throw new Error("Chat is missing its gateway API URL configuration.");
    }

    const token = await getAccessToken();
    const response = await fetch(`${apiBaseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    const responseText = await response.text();
    let data = null;

    if (responseText) {
      try {
        data = JSON.parse(responseText);
      } catch {
        if (response.ok) {
          throw new Error("The gateway returned an invalid response.");
        }
      }
    }

    if (!response.ok) {
      const detail =
        data && typeof data.detail === "string"
          ? data.detail
          : `Chat request failed (${response.status}).`;
      throw new Error(detail);
    }

    if (!data || typeof data !== "object") {
      throw new Error("The gateway returned an invalid response.");
    }

    return data;
  }

  function showApproval(details, id) {
    awaitingApproval = true;
    setBusy(false);

    const card = document.createElement("section");
    card.className = "approval";

    const title = document.createElement("div");
    title.className = "approval-title";
    title.textContent = "Please review this booking";

    const detailText = document.createElement("pre");
    detailText.className = "approval-details";
    detailText.textContent = JSON.stringify(details, null, 2);

    const actions = document.createElement("div");
    actions.className = "approval-actions";

    const approveButton = document.createElement("button");
    approveButton.type = "button";
    approveButton.textContent = "Approve";
    approveButton.addEventListener("click", () => {
      submitDecision(id, "approve", card);
    });

    const rejectButton = document.createElement("button");
    rejectButton.type = "button";
    rejectButton.className = "reject";
    rejectButton.textContent = "Reject";
    rejectButton.addEventListener("click", () => {
      submitDecision(id, "reject", card);
    });

    actions.append(approveButton, rejectButton);
    card.append(title, detailText, actions);
    messages.appendChild(card);
    messages.scrollTop = messages.scrollHeight;
  }

  function displayResponse(data) {
    if (typeof data.session_id !== "string" || !data.session_id) {
      throw new Error("The gateway did not return a chat session.");
    }

    sessionId = data.session_id;

    if (typeof data.reply === "string" && data.reply) {
      addMessage(data.reply);
    }

    if (data.status === "pending_approval" && data.approval) {
      showApproval(data.approval, sessionId);
      return;
    }

    awaitingApproval = false;
    setBusy(false);
  }

  async function submitDecision(id, decision, card) {
    if (busy) return;

    setBusy(true);
    card.querySelectorAll("button").forEach((button) => {
      button.disabled = true;
    });

    const pending = addMessage(
      decision === "approve" ? "Submitting approval..." : "Sending rejection...",
      "pending"
    );

    try {
      const data = await apiRequest(
        `/chat/${encodeURIComponent(id)}/decision`,
        { decision }
      );

      pending.remove();
      card.remove();
      awaitingApproval = false;
      displayResponse(data);
    } catch (error) {
      pending.remove();
      addMessage(error.message || "Could not submit your decision.", "error");
      card.querySelectorAll("button").forEach((button) => {
        button.disabled = false;
      });
      setBusy(false);
    }
  }

  launcher.addEventListener("click", () => {
    panel.hidden = !panel.hidden;

    if (!panel.hidden) {
      input.focus();
    }
  });

  closeButton.addEventListener("click", () => {
    panel.hidden = true;
    launcher.focus();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message || busy || awaitingApproval) return;

    addMessage(message, "user");
    input.value = "";
    setBusy(true);

    const pending = addMessage("One moment...", "pending");

    try {
      const data = await apiRequest("/chat", {
        message,
        ...(sessionId ? { session_id: sessionId } : {}),
      });

      pending.remove();
      displayResponse(data);
    } catch (error) {
      pending.remove();
      addMessage(error.message || "Could not send your message.", "error");
      setBusy(false);
    }
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  addMessage("Hi! Sign in to Fixji and ask me how I can help.");
})();