/* Reviewer desk. Fetches files.json from this manuscript's endpoint. */

const treeEl = document.getElementById("file-tree");
const labelEl = document.getElementById("viewer-label");
const objectEl = document.getElementById("pdf-viewer");
const imageWrap = document.getElementById("image-wrap");
const imageEl = document.getElementById("image-viewer");
const textEl = document.getElementById("text-view");
const emptyEl = document.getElementById("empty");
const titleEl = document.getElementById("desk-title");
const stampEl = document.getElementById("desk-stamp");

function hideAll() {
  objectEl.style.display = "none";
  objectEl.removeAttribute("data");
  imageWrap.style.display = "none";
  textEl.style.display = "none";
  emptyEl.style.display = "none";
}

function loadFile(file) {
  hideAll();
  labelEl.textContent = file.url || file.name;
  document.querySelectorAll(".file-item").forEach((el) => el.classList.remove("active"));
  if (file._btn) file._btn.classList.add("active");

  if (file.type === "pdf") {
    objectEl.style.display = "block";
    objectEl.setAttribute("data", `${file.url}#toolbar=1&scrollbar=1&navpanes=1`);
    return;
  }
  if (file.type === "image") {
    imageWrap.style.display = "flex";
    imageEl.src = file.url;
    return;
  }
  fetch(file.url).then((r) => {
    if (!r.ok) throw new Error(r.status);
    return r.text();
  }).then((text) => {
    textEl.style.display = "block";
    textEl.textContent = text;
  }).catch(() => {
    emptyEl.style.display = "block";
    emptyEl.textContent = "Could not load " + file.url;
  });
}

function renderNodes(nodes, host) {
  for (const node of nodes) {
    if (node.type === "dir") {
      const h = document.createElement("div");
      h.className = "dir-name";
      h.textContent = node.name;
      host.appendChild(h);
      renderNodes(node.children || [], host);
      continue;
    }
    const b = document.createElement("button");
    b.type = "button";
    b.className = "file-item";
    const meta = node.bytes
      ? `${(node.bytes / 1024).toFixed(0)} KB`
      : (node.label || "");
    b.innerHTML = `<span>${node.name}</span><span class="meta">${meta}</span>`;
    node._btn = b;
    b.addEventListener("click", () => loadFile(node));
    host.appendChild(b);
  }
}

function findOpen(nodes, url) {
  for (const node of nodes) {
    if (node.type === "dir") {
      const hit = findOpen(node.children || [], url);
      if (hit) return hit;
    } else if (node.url === url) {
      return node;
    }
  }
  return null;
}

function firstPdf(nodes) {
  for (const node of nodes) {
    if (node.type === "dir") {
      const hit = firstPdf(node.children || []);
      if (hit) return hit;
    } else if (node.type === "pdf") {
      return node;
    }
  }
  return null;
}

fetch("./files.json")
  .then((r) => r.json())
  .then((data) => {
    titleEl.textContent = data.title || "Manuscript";
    stampEl.textContent = [data.target, data.received].filter(Boolean).join(" · ");
    renderNodes(data.tree || [], treeEl);
    const start = findOpen(data.tree || [], data.open) || firstPdf(data.tree || []);
    if (start) loadFile(start);
  })
  .catch((err) => {
    emptyEl.style.display = "block";
    emptyEl.textContent = "files.json missing. Run tools/build_desks.py. " + err;
  });
