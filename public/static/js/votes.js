const csrfToken = document.querySelector(
    'meta[name="csrf-token"]'
).content;

document.querySelectorAll(".vote").forEach((widget) => {
    const buttons = widget.querySelectorAll(".vote__btn");
    const errorElement = widget.querySelector(".vote__error");

    function updateButtons() {
        buttons.forEach((item) => {
            const selected = item.getAttribute("aria-pressed") === "true";
            const canVote = widget.dataset.canVote === "true";
            item.disabled = !canVote || selected;
            item.title = !canVote
                ? "Войдите, чтобы голосовать"
                : selected ? "Вы уже поставили такую оценку" : "";
        });
    }

    updateButtons();

    buttons.forEach((button) => {
        button.addEventListener("click", async () => {
            const url = widget.dataset.voteUrl;
            const value = button.dataset.value;

            errorElement.hidden = true;
            errorElement.textContent = "";

            buttons.forEach((item) => {
                item.disabled = true;
            });

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                    body: new URLSearchParams({ value: value }),
                    mode: "same-origin",
                });

                if (response.status === 403) {
                    throw new Error(
                        "Запрос отклонён. Обновите страницу и попробуйте снова."
                    );
                }

                if (response.status === 401) {
                    widget.dataset.canVote = "false";
                    throw new Error("Сессия завершена. Войдите в аккаунт и обновите страницу.");
                }

                if (!response.headers.get("content-type")?.includes("application/json")) {
                    throw new Error("Сервер вернул неожиданный ответ. Попробуйте позже.");
                }

                const data = await response.json();

                if (!response.ok) {
                    let message = data.error;

                    if (!message && data.errors) {
                        message = Object.values(data.errors)
                            .flat()
                            .map((error) => error.message)
                            .join(" ");
                    }

                    throw new Error(
                        message || "Не удалось сохранить оценку."
                    );
                }

                widget.querySelector(".vote__count").textContent =
                    data.rating;

                widget.classList.toggle(
                    "vote--liked",
                    data.vote_state === "liked"
                );

                widget.classList.toggle(
                    "vote--disliked",
                    data.vote_state === "disliked"
                );

                buttons.forEach((item) => {
                    const selected =
                        (item.dataset.value === "1" &&
                            data.vote_state === "liked") ||
                        (item.dataset.value === "-1" &&
                            data.vote_state === "disliked");

                    item.setAttribute("aria-pressed", String(selected));
                });
            } catch (error) {
                errorElement.textContent = error instanceof TypeError
                    ? "Не удалось связаться с сервером. Проверьте соединение и повторите попытку."
                    : error.message;
                errorElement.hidden = false;
            } finally {
                updateButtons();
            }
        });
    });
});