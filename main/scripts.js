document.addEventListener('DOMContentLoaded', () => {
    // Пример: Добавление товара в избранное
    document.querySelectorAll('.favorite-button').forEach(button => {
        button.addEventListener('click', () => {
            alert('Товар добавлен в избранное!');
        });
    });
});
