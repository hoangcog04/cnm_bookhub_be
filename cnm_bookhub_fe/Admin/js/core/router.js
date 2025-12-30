const ScriptLoader = {
  loadedScripts: new Set(),

  load: function (path) {
    if (this.loadedScripts.has(path)) return Promise.resolve();

    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = path;
      script.onload = () => {
        this.loadedScripts.add(path);
        resolve();
      };
      script.onerror = () => reject(new Error(`Không thể tải script: ${path}`));
      document.body.appendChild(script);
    });
  }
};

const Router = {
  currentRoute: "books",
  routes: {},
  register: function (route, handler) {
    this.routes[route] = handler
  },

  queryParams: {},

  navigate: function (fullRoute) {
    // Split route and query params
    const [path, queryString] = fullRoute.split("?");
    this.queryParams = {};

    if (queryString) {
      const params = new URLSearchParams(queryString);
      for (const [key, value] of params) {
        this.queryParams[key] = value;
      }
    }

    if (!this.routes[path]) {
      console.error(`Route ${path} not found`);
      return;
    }

    this.currentRoute = path;
    // Update hash without triggering hashchange event loop if possible, 
    // but here we usually rely on hashchange unless called programmatically.
    // If called programmatically, we should update the URL.
    if (window.location.hash.slice(2) !== fullRoute) {
      window.location.hash = "/" + fullRoute;
      return; // Hash change will trigger listener, so we stop here
    }

    this.render(path);
    this.updateActiveNav(path);
  },

  render: function (route) {
    const handler = this.routes[route];
    handler();
  },

  updateActiveNav: (route) => {
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
    });

    // Handle nested routes or exact match
    // Simplified: just match exact data-route
    const activeNav = document.querySelector(`[data-route="${route}"]`);
    if (activeNav) {
      activeNav.classList.add("active");
    }
  },

  init: function () {
    window.addEventListener("hashchange", () => {
      const fullRoute = window.location.hash.slice(2) || "books";
      this.navigate(fullRoute);
    });

    const fullRoute = window.location.hash.slice(2) || "books";
    this.navigate(fullRoute);
  },
};