// Retail Sales Analytics System - frontend logic
// Works when opened as a file (talks to Flask on port 5000)
// and when served by Flask itself (same origin).
// KPIs and charts are built from the filtered sales rows.

const API = window.location.protocol === "file:" ? "http://127.0.0.1:5000" : "";

let monthlyChart = null;
let categoryChart = null;
let products = [];

const $ = (id) => document.getElementById(id);

// ---------- helpers ----------

function money(n) {
  return Number(n).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function showError(msg) {
  const box = $("errorBanner");
  box.textContent = msg;
  box.classList.remove("hidden");
}

function clearError() {
  $("errorBanner").classList.add("hidden");
}

async function getJSON(path) {
  const res = await fetch(API + path);
  if (!res.ok) {
    throw new Error("Request failed (" + res.status + "): " + path);
  }
  return res.json();
}

async function postJSON(path, payload) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data: data };
}

function toList(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object") {
    const firstArray = Object.values(data).find(Array.isArray);
    if (firstArray) return firstArray;
  }
  return [];
}

function fillSelect(select, items, valueFn, textFn, placeholder) {
  select.innerHTML = "";
  if (placeholder) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = placeholder;
    select.appendChild(opt);
  }
  items.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = valueFn(item);
    opt.textContent = textFn(item);
    select.appendChild(opt);
  });
}

function setMessage(id, text, kind) {
  const el = $(id);
  el.textContent = text;
  el.className = kind || "status";
}

// ---------- category checkboxes ----------

// one fixed colour per category, so a bar keeps its colour when others are hidden
const CATEGORY_COLORS = ["#2f6fed", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#db2777"];
let allCategories = [];

function selectedCategories() {
  return Array.from($("fCategories").querySelectorAll("input:checked")).map((i) => i.value);
}

function buildCategoryBoxes(categories) {
  const keep = selectedCategories();
  const box = $("fCategories");
  box.innerHTML = "";
  categories.forEach((name) => {
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = name;
    input.checked = keep.includes(name);
    input.addEventListener("change", () => {
      clearError();
      loadSales().catch((err) => showError(err.message));
    });
    label.appendChild(input);
    label.appendChild(document.createTextNode(" " + name));
    box.appendChild(label);
  });

  // suggestions for the Add Product category box
  const list = $("categoryOptions");
  list.innerHTML = "";
  categories.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    list.appendChild(opt);
  });
}

// ---------- KPIs (from the filtered rows) ----------

function updateKpis(rows) {
  const revenue = rows.reduce((sum, r) => sum + Number(r.revenue), 0);
  const units = rows.reduce((sum, r) => sum + Number(r.quantity), 0);
  const orders = new Set(rows.map((r) => r.sale_id)).size;
  const aov = orders ? revenue / orders : 0;

  $("kpiRevenue").textContent = money(revenue);
  $("kpiOrders").textContent = orders;
  $("kpiUnits").textContent = units;
  $("kpiAov").textContent = money(aov);
}

// ---------- charts (from the filtered rows) ----------

function sumBy(rows, keyFn) {
  const totals = {};
  rows.forEach((r) => {
    const key = keyFn(r);
    totals[key] = (totals[key] || 0) + Number(r.revenue);
  });
  return totals;
}

function updateCharts(rows) {
  // monthly: sale_date is "YYYY-MM-DD", so the first 7 characters are the month
  const monthly = sumBy(rows, (r) => String(r.sale_date).slice(0, 7));
  const monthLabels = Object.keys(monthly).sort();
  const monthValues = monthLabels.map((m) => Math.round(monthly[m] * 100) / 100);

  // category: only categories present in the rows (= the ticked ones), highest first
  const byCat = sumBy(rows, (r) => r.category);
  const catLabels = Object.keys(byCat).sort((a, b) => byCat[b] - byCat[a]);
  const catValues = catLabels.map((c) => Math.round(byCat[c] * 100) / 100);
  const catColors = catLabels.map((c) => {
    const i = allCategories.indexOf(c);
    return CATEGORY_COLORS[(i < 0 ? 0 : i) % CATEGORY_COLORS.length];
  });

  if (monthlyChart) monthlyChart.destroy();
  if (categoryChart) categoryChart.destroy();

  monthlyChart = new Chart($("monthlyChart"), {
    type: "line",
    data: {
      labels: monthLabels,
      datasets: [
        {
          label: "Revenue",
          data: monthValues,
          borderColor: "#2f6fed",
          backgroundColor: "rgba(47, 111, 237, 0.15)",
          fill: true,
          tension: 0.25,
        },
      ],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });

  categoryChart = new Chart($("categoryChart"), {
    type: "bar",
    data: {
      labels: catLabels,
      datasets: [{ label: "Revenue", data: catValues, backgroundColor: catColors }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });
}

// ---------- sales table ----------

function buildFilterParams() {
  const params = new URLSearchParams();
  const q = $("fSearch").value.trim();
  if (q) params.set("q", q);
  if ($("fFrom").value) params.set("date_from", $("fFrom").value);
  if ($("fTo").value) params.set("date_to", $("fTo").value);
  const cats = selectedCategories();
  if (cats.length) params.set("category", cats.join(","));
  return params;
}

function buildSalesQuery() {
  const s = buildFilterParams().toString();
  return s ? "?" + s : "";
}

async function loadSales() {
  const status = $("salesStatus");
  const body = $("salesBody");
  status.textContent = "Loading...";
  body.innerHTML = "";

  const rows = toList(await getJSON("/api/sales" + buildSalesQuery()));

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    const cells = [
      r.sale_id,
      r.sale_date,
      r.customer,
      r.product,
      r.category,
      r.quantity,
      money(r.unit_price),
      (Number(r.discount_rate) * 100).toFixed(1) + "%",
      money(r.revenue),
      r.payment_method,
    ];
    cells.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });

  status.textContent = rows.length
    ? rows.length + " row(s) shown."
    : "No sales match these filters.";

  updateKpis(rows);
  updateCharts(rows);
}

// ---------- Excel download ----------

function downloadExcel() {
  const s = buildFilterParams().toString();
  window.location.href = API + "/api/export/excel" + (s ? "?" + s : "");
}

// ---------- dropdown loading ----------

async function loadCustomers(selectId) {
  const customers = toList(await getJSON("/api/customers"));
  fillSelect(
    $("nCustomer"),
    customers,
    (c) => c.customer_id,
    (c) => c.full_name,
    "Select customer"
  );
  if (selectId) $("nCustomer").value = String(selectId);
}

async function loadProductsAndCategories(selectId) {
  const [prodData, catData] = await Promise.all([
    getJSON("/api/products"),
    getJSON("/api/categories"),
  ]);
  products = toList(prodData);
  const catName = (c) => (typeof c === "string" ? c : c.category || c.name);
  allCategories = toList(catData).map(catName);

  fillSelect(
    $("nProduct"),
    products,
    (p) => p.product_id,
    (p) => p.product_name,
    "Select product"
  );
  if (selectId) $("nProduct").value = String(selectId);

  buildCategoryBoxes(allCategories);
}

// ---------- new sale form ----------

function updatePricePreview() {
  const preview = $("pricePreview");
  const product = products.find((p) => String(p.product_id) === $("nProduct").value);
  if (!product) {
    preview.textContent = "";
    return;
  }
  const qty = Number($("nQty").value) || 0;
  const disc = Number($("nDiscount").value) || 0;
  const total = product.unit_price * qty * (1 - disc / 100);
  preview.textContent =
    "Unit price: " + money(product.unit_price) + "  |  Estimated total: " + money(total);
}

function setFormMessage(text, kind) {
  const el = $("formMessage");
  el.textContent = text;
  el.className = kind || "";
}

async function saveSale() {
  const customerId = $("nCustomer").value;
  const productId = $("nProduct").value;
  const quantity = Number($("nQty").value);
  const discountPercent = Number($("nDiscount").value);
  const payment = $("nPayment").value;
  const saleDate = $("nDate").value;

  if (!customerId) return setFormMessage("Please select a customer.", "error");
  if (!productId) return setFormMessage("Please select a product.", "error");
  if (!Number.isInteger(quantity) || quantity < 1)
    return setFormMessage("Quantity must be a whole number of at least 1.", "error");
  if (isNaN(discountPercent) || discountPercent < 0 || discountPercent > 100)
    return setFormMessage("Discount must be between 0 and 100.", "error");
  if (!saleDate) return setFormMessage("Please choose a date.", "error");

  const payload = {
    customer_id: Number(customerId),
    product_id: Number(productId),
    quantity: quantity,
    discount_rate: discountPercent / 100,
    payment_method: payment,
    sale_date: saleDate,
  };

  const button = $("btnSave");
  button.disabled = true;
  setFormMessage("Saving...", "");

  try {
    const result = await postJSON("/api/sales", payload);
    if (!result.ok) {
      setFormMessage(result.data.message || result.data.error || "Could not save the sale.", "error");
      return;
    }

    setFormMessage("Sale created (ID " + result.data.sale_id + ").", "success");
    $("nQty").value = 1;
    $("nDiscount").value = 0;
    updatePricePreview();
    await refreshAll();
  } catch (err) {
    setFormMessage("Network error: " + err.message, "error");
  } finally {
    button.disabled = false;
  }
}

// ---------- add customer / add product ----------

async function addCustomer() {
  const payload = {
    full_name: $("cName").value.trim(),
    email: $("cEmail").value.trim(),
    city: $("cCity").value.trim(),
    state: $("cState").value.trim(),
  };
  if (!payload.full_name) return setMessage("customerMessage", "Please enter the full name.", "error");
  if (!payload.email) return setMessage("customerMessage", "Please enter the email.", "error");
  if (!payload.city || !payload.state)
    return setMessage("customerMessage", "Please enter city and state.", "error");

  const button = $("btnAddCustomer");
  button.disabled = true;
  setMessage("customerMessage", "Saving...", "status");
  try {
    const result = await postJSON("/api/customers", payload);
    if (!result.ok) {
      setMessage("customerMessage", result.data.message || "Could not add the customer.", "error");
      return;
    }
    setMessage("customerMessage", "Customer added (ID " + result.data.customer_id + ").", "success");
    ["cName", "cEmail", "cCity", "cState"].forEach((id) => ($(id).value = ""));
    await loadCustomers(result.data.customer_id);
  } catch (err) {
    setMessage("customerMessage", "Network error: " + err.message, "error");
  } finally {
    button.disabled = false;
  }
}

async function addProduct() {
  const price = Number($("pPrice").value);
  const payload = {
    product_name: $("pName").value.trim(),
    category: $("pCategory").value.trim(),
    unit_price: price,
  };
  if (!payload.product_name) return setMessage("productMessage", "Please enter the product name.", "error");
  if (!payload.category) return setMessage("productMessage", "Please enter a category.", "error");
  if (!(price > 0)) return setMessage("productMessage", "Price must be greater than 0.", "error");

  const button = $("btnAddProduct");
  button.disabled = true;
  setMessage("productMessage", "Saving...", "status");
  try {
    const result = await postJSON("/api/products", payload);
    if (!result.ok) {
      setMessage("productMessage", result.data.message || "Could not add the product.", "error");
      return;
    }
    setMessage("productMessage", "Product added (ID " + result.data.product_id + ").", "success");
    ["pName", "pCategory", "pPrice"].forEach((id) => ($(id).value = ""));
    await loadProductsAndCategories(result.data.product_id);
    updatePricePreview();
  } catch (err) {
    setMessage("productMessage", "Network error: " + err.message, "error");
  } finally {
    button.disabled = false;
  }
}

// ---------- startup ----------

async function refreshAll() {
  clearError();
  try {
    await loadSales();
  } catch (err) {
    showError("Could not load data. Is the Flask server running? (" + err.message + ")");
  }
}

function resetFilters() {
  $("fSearch").value = "";
  $("fFrom").value = "";
  $("fTo").value = "";
  $("fCategories").querySelectorAll("input").forEach((i) => (i.checked = false));
  loadSales().catch((err) => showError(err.message));
}

async function init() {
  $("nDate").value = new Date().toISOString().slice(0, 10);

  $("btnApply").addEventListener("click", () => {
    clearError();
    loadSales().catch((err) => showError(err.message));
  });
  $("btnReset").addEventListener("click", resetFilters);
  $("btnExcel").addEventListener("click", downloadExcel);
  $("btnSave").addEventListener("click", saveSale);
  $("btnAddCustomer").addEventListener("click", addCustomer);
  $("btnAddProduct").addEventListener("click", addProduct);
  $("nProduct").addEventListener("change", updatePricePreview);
  $("nQty").addEventListener("input", updatePricePreview);
  $("nDiscount").addEventListener("input", updatePricePreview);

  try {
    await Promise.all([loadCustomers(), loadProductsAndCategories()]);
  } catch (err) {
    showError("Could not load dropdown lists: " + err.message);
  }
  await refreshAll();
}

document.addEventListener("DOMContentLoaded", init);