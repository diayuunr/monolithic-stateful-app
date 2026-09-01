const loginPage = document.getElementById("login-page");
const registerPage = document.getElementById("register-page");
const appPage = document.getElementById("app-page");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const puisiForm = document.getElementById("puisi-form");
const loginMessage = document.getElementById("login-message");
const registerMessage = document.getElementById("register-message");
const puisiMessage = document.getElementById("puisi-message");
const userName = document.getElementById("user-name");
const puisiList = document.getElementById("puisi-list");

document.getElementById("show-register").addEventListener("click", () => {
    loginPage.style.display = "none";
    registerPage.style.display = "block";
});

document.getElementById("show-login").addEventListener("click", () => {
    registerPage.style.display = "none";
    loginPage.style.display = "block";
});

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("register-username").value;
    const nama = document.getElementById("register-nama").value;
    const password = document.getElementById("register-password").value;
    const no_id = document.getElementById("register-no-id").value;
    try {
        const response = await fetch("/?action=register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, nama, password, no_id})
        });
        const data = await response.json();
        if (response.ok) {
            registerMessage.textContent = data.message;
            registerForm.reset();
            setTimeout(() => {
                registerPage.style.display = "none";
                loginPage.style.display = "block";
                registerMessage.textContent = "";
            }, 1000);
        } else {
            registerMessage.textContent = data.message;
        }
    } catch (error) {
        console.error(error);
        registerMessage.textContent = "Tidak dapat terhubung ke server";
    }
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    try {
        const response = await fetch("/?action=login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        if (response.ok) {
            userName.textContent = data.nama;
            loginPage.style.display = "none";
            registerPage.style.display = "none";
            appPage.style.display = "block";
            loginForm.reset();
            loadPuisi();
        } else {
            loginMessage.textContent = data.message;
        }
    } catch (error) {
        console.error(error);
        loginMessage.textContent = "Tidak dapat terhubung ke server";
    }
});

puisiForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const judul = document.getElementById("judul").value;
    const isi = document.getElementById("isi").value;
    const kategori = document.getElementById("kategori").value;
    const keyword = document.getElementById("keyword").value;
    try {
        const response = await fetch("/?action=submit_puisi", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({judul, isi, kategori, keyword})
        });
        const data = await response.json();
        if (response.ok) {
            puisiMessage.textContent = data.message;
            puisiForm.reset();
            loadPuisi();
        } else {
            puisiMessage.textContent = data.message;
        }
    } catch (error) {
        console.error(error);
        puisiMessage.textContent = "Tidak dapat terhubung ke server";
    }
});

async function loadPuisi() {
    try {
        const response = await fetch("/?action=daftar_puisi", {
            method: "GET",
            credentials: "include"
        });
        const data = await response.json();
        if (!response.ok) {
            puisiList.innerHTML = `<p>${data.message}</p>`;
            return;
        }
        puisiList.innerHTML = "";
        if (data.data.length === 0) {
            puisiList.innerHTML = "<p>Belum ada puisi.</p>";
            return;
        }
        data.data.forEach((puisi) => {
            const item = document.createElement("div");
            item.className = "puisi-item";
            item.innerHTML = `
                <h3>${puisi.judul}</h3>
                <p>${puisi.isi}</p>
                <p><strong>Kategori:</strong> ${puisi.kategori}</p>
                <p><strong>Keyword:</strong> ${puisi.keyword || "-"}</p>
                <p class="puisi-meta">Tanggal: ${puisi.tgl_submit}</p>
            `;
            puisiList.appendChild(item);
        });
    } catch (error) {
        console.error(error);
        puisiList.innerHTML = "<p>Tidak dapat terhubung ke server.</p>";
    }
}

document.getElementById("logout-button").addEventListener("click", async () => {
    try {
        const response = await fetch("/?action=logout", {
            method: "POST",
            credentials: "include"
        });
        const data = await response.json();
        if (response.ok) {
            appPage.style.display = "none";
            loginPage.style.display = "block";
            userName.textContent = "";
            puisiList.innerHTML = "";
            puisiMessage.textContent = "";
            loginMessage.textContent = data.message;
        } else {
            puisiMessage.textContent = data.message;
        }
    } catch (error) {
        console.error(error);
        puisiMessage.textContent = "Tidak dapat terhubung ke server";
    }
});