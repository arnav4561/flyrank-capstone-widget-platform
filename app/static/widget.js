(function () {
    "use strict";

    const script = document.currentScript;

    if (!script) {
        console.error("FlyRank widget: unable to find script element.");
        return;
    }

    const publicId = script.dataset.widget;

    if (!publicId) {
        console.error("FlyRank widget: missing data-widget attribute.");
        return;
    }

    const apiBaseUrl =
        script.dataset.apiBase ||
        new URL(script.src).origin;

    const containerId =
        script.dataset.container || "flyrank-widget";

    function createElement(tag, attributes = {}, text = "") {
        const element = document.createElement(tag);

        Object.entries(attributes).forEach(([key, value]) => {
            if (key === "className") {
                element.className = value;
            } else {
                element.setAttribute(key, value);
            }
        });

        if (text) {
            element.textContent = text;
        }

        return element;
    }

    function renderMessage(container, message, type = "info") {
        const messageElement = createElement(
            "div",
            {
                className: `flyrank-message flyrank-message-${type}`,
            },
            message
        );

        container.appendChild(messageElement);
    }

    function getInputType(field) {
        if (field.type === "email") {
            return "email";
        }

        if (field.type === "number") {
            return "number";
        }

        return "text";
    }

    function renderWidget(container, config) {
        container.innerHTML = "";

        const wrapper = createElement("div", {
            className: "flyrank-widget",
        });

        const title = createElement(
            "h2",
            {
                className: "flyrank-widget-title",
            },
            config.title
        );

        wrapper.appendChild(title);

        if (config.description) {
            const description = createElement(
                "p",
                {
                    className: "flyrank-widget-description",
                },
                config.description
            );

            wrapper.appendChild(description);
        }

        const form = createElement("form", {
            className: "flyrank-widget-form",
        });

        (config.fields || []).forEach((field) => {
            if (!field || !field.name) {
                return;
            }

            const fieldWrapper = createElement("div", {
                className: "flyrank-field",
            });

            const label = createElement(
                "label",
                {
                    className: "flyrank-label",
                    for: `flyrank-${field.name}`,
                },
                field.name
            );

            if (field.required) {
                label.textContent += " *";
            }

            const input = createElement("input", {
                id: `flyrank-${field.name}`,
                name: field.name,
                type: getInputType(field),
                className: "flyrank-input",
            });

            if (field.required) {
                input.required = true;
            }

            fieldWrapper.appendChild(label);
            fieldWrapper.appendChild(input);
            form.appendChild(fieldWrapper);
        });

        // Honeypot field.
        const honeypotWrapper = createElement("div", {
            className: "flyrank-honeypot",
            "aria-hidden": "true",
        });

        const honeypot = createElement("input", {
            type: "text",
            name: "website",
            tabindex: "-1",
            autocomplete: "off",
        });

        honeypotWrapper.appendChild(honeypot);
        form.appendChild(honeypotWrapper);

        const submitButton = createElement(
            "button",
            {
                type: "submit",
                className: "flyrank-submit",
            },
            config.button_text || "Submit"
        );

        form.appendChild(submitButton);

        const status = createElement("div", {
            className: "flyrank-status",
            role: "status",
        });

        form.appendChild(status);

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            status.textContent = "";
            submitButton.disabled = true;
            submitButton.textContent = "Sending...";

            const data = {};

            (config.fields || []).forEach((field) => {
                if (!field || !field.name) {
                    return;
                }

                const input = form.elements[field.name];

                if (input) {
                    data[field.name] = input.value;
                }
            });

            const idempotencyKey =
                window.crypto && window.crypto.randomUUID
                    ? window.crypto.randomUUID()
                    : `${Date.now()}-${Math.random()}`;

            try {
                const response = await fetch(
                    `${apiBaseUrl}/api/v1/public/widgets/${publicId}/submissions`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Idempotency-Key": idempotencyKey,
                        },
                        body: JSON.stringify({
                            data,
                            honeypot: honeypot.value,
                        }),
                    }
                );

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(
                        result.detail || "Submission failed."
                    );
                }

                status.textContent =
                    "Thanks! Your submission was received.";

                status.className =
                    "flyrank-status flyrank-status-success";

                form.reset();
            } catch (error) {
                console.error(
                    "FlyRank widget submission error:",
                    error
                );

                status.textContent =
                    error.message || "Something went wrong.";

                status.className =
                    "flyrank-status flyrank-status-error";
            } finally {
                submitButton.disabled = false;
                submitButton.textContent =
                    config.button_text || "Submit";
            }
        });

        wrapper.appendChild(form);
        container.appendChild(wrapper);
    }

    function addStyles() {
        if (document.getElementById("flyrank-widget-styles")) {
            return;
        }

        const style = document.createElement("style");

        style.id = "flyrank-widget-styles";

        style.textContent = `
            .flyrank-widget {
                max-width: 420px;
                padding: 24px;
                border: 1px solid #ddd;
                border-radius: 12px;
                background: #fff;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
                font-family: Arial, sans-serif;
                box-sizing: border-box;
            }

            .flyrank-widget *,
            .flyrank-widget *::before,
            .flyrank-widget *::after {
                box-sizing: border-box;
            }

            .flyrank-widget-title {
                margin: 0 0 8px;
                font-size: 24px;
            }

            .flyrank-widget-description {
                margin: 0 0 20px;
                color: #666;
            }

            .flyrank-field {
                margin-bottom: 16px;
            }

            .flyrank-label {
                display: block;
                margin-bottom: 6px;
                font-weight: 600;
            }

            .flyrank-input {
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 15px;
            }

            .flyrank-submit {
                width: 100%;
                padding: 11px 16px;
                border: 0;
                border-radius: 6px;
                background: #111;
                color: #fff;
                font-size: 15px;
                cursor: pointer;
            }

            .flyrank-submit:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .flyrank-status {
                margin-top: 12px;
                font-size: 14px;
            }

            .flyrank-status-success {
                color: #18794e;
            }

            .flyrank-status-error {
                color: #b42318;
            }

            .flyrank-honeypot {
                position: absolute !important;
                left: -10000px !important;
                width: 1px !important;
                height: 1px !important;
                overflow: hidden !important;
            }
        `;

        document.head.appendChild(style);
    }

    async function initialize() {
        addStyles();

        let container = document.getElementById(containerId);

        if (!container) {
            container = document.createElement("div");
            container.id = containerId;
            script.parentNode.insertBefore(
                container,
                script.nextSibling
            );
        }

        container.innerHTML = "Loading widget...";

        try {
            const response = await fetch(
                `${apiBaseUrl}/api/v1/public/widgets/${publicId}`
            );

            if (!response.ok) {
                throw new Error(
                    `Unable to load widget (${response.status}).`
                );
            }

            const config = await response.json();

            renderWidget(container, config);
        } catch (error) {
            console.error(
                "FlyRank widget initialization error:",
                error
            );

            container.innerHTML = "";

            renderMessage(
                container,
                "Unable to load this widget.",
                "error"
            );
        }
    }

    initialize();
})();