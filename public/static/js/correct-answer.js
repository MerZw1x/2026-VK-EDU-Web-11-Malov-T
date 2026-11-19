{
    const section = document.querySelector(".answers");

    if (section) {
        const checkboxes = section.querySelectorAll(".js-correct-answer");
        const errorElement = section.querySelector(".correct-answer-error");
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        let sessionExpired = false;

        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", async () => {
                const previousState = !checkbox.checked;
                errorElement.hidden = true;
                errorElement.textContent = "";
                checkboxes.forEach((item) => { item.disabled = true; });

                try {
                    const response = await fetch(section.dataset.correctUrl, {
                        method: "POST",
                        headers: { "X-CSRFToken": csrfToken },
                        body: new URLSearchParams({ answer_id: checkbox.dataset.answerId }),
                        mode: "same-origin",
                    });
                    if (response.status === 401) {
                        sessionExpired = true;
                        throw new Error("Сессия завершена. Войдите в аккаунт и обновите страницу.");
                    }
                    if (response.status === 403) {
                        throw new Error("Запрос отклонён. Обновите страницу и попробуйте снова.");
                    }
                    if (!response.headers.get("content-type")?.includes("application/json")) {
                        throw new Error("Сервер вернул неожиданный ответ. Попробуйте позже.");
                    }
                    const data = await response.json();
                    if (!response.ok) {
                        const message = data.error || (data.errors && Object.values(data.errors)
                            .flat().map((error) => error.message).join(" "));
                        throw new Error(message || "Не удалось изменить правильный ответ.");
                    }

                    checkboxes.forEach((item) => {
                        const selected = item.dataset.answerId === String(data.answer_id) && data.is_correct;
                        item.checked = selected;
                        item.closest(".answer-card").classList.toggle("answer-card--correct", selected);
                    });
                } catch (error) {
                    checkbox.checked = previousState;
                    errorElement.textContent = error instanceof TypeError
                        ? "Не удалось связаться с сервером. Проверьте соединение и повторите попытку."
                        : error.message;
                    errorElement.hidden = false;
                } finally {
                    checkboxes.forEach((item) => { item.disabled = sessionExpired; });
                }
            });
        });
    }
}
