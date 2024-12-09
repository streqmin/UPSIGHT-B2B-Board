document.addEventListener('DOMContentLoaded', function () {
    const logoutButton = document.getElementById('logout-button');

    if (logoutButton) {
        const logoutUrl = logoutButton.getAttribute('data-logout-url');
        const loginUrl = logoutButton.getAttribute('data-login-url');

        logoutButton.addEventListener('click', async function (event) {
            event.preventDefault();

            try {
                const response = await fetch(logoutUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include'
                });

                if (response.ok) {
                    alert('로그아웃되었습니다.');
                    window.location.href = loginUrl; // 로그아웃 후 로그인 페이지로 리다이렉트
                } else {
                    alert('로그아웃에 실패했습니다.');
                }
            } catch (error) {
                console.error('Error during logout:', error);
                alert('오류가 발생했습니다.');
            }
        });
    }
});
