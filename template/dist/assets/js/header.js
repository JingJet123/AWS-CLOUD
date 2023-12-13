

const template = document.createElement('template')

template.innerHTML = `

<header class="mb-5">
<div class="header-top">
  <div class="container">
      <h3 class="heading3aaa">FOCS ITP OnMyFinger</h3>
    <div class="header-top-right">
      <div class="dropdown mx-3">
        <a
          href="#"
          id="topbarUserDropdown"
          class="user-dropdown d-flex align-items-center dropend dropdown-toggle"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          <div class="avatar avatar-md2">
            <img src="assets/images/faces/1.jpg" alt="Avatar" />
          </div>
          <div class="text">
            <h6 class="user-dropdown-name">Log In / Sign Up</h6>
            <p class="user-dropdown-status text-sm text-muted">
              Please Sign in according to your role
            </p>
          </div>
        </a>
        <ul
          class="dropdown-menu dropdown-menu-end shadow-lg"
          aria-labelledby="topbarUserDropdown"
        >
          <li><a class="dropdown-item" href="/studentLogin">Student</a></li>
          <li><a class="dropdown-item" href="/supervisorLogin">Supervisor</a></li>
          <li><a class="dropdown-item" href="/companyLogin">Company</a></li>
          <li><a class="dropdown-item" href="/adminLogin">ITP Committee</a></li>

        </ul>
      </div>

      <!-- Burger button responsive -->
      <a href="#" class="burger-btn d-block d-xl-none">
        <i class="bi bi-justify fs-3"></i>
      </a>
    </div>
  </div>
</div> 
<nav class="main-navbar">
  <div class="container">
    <ul>
      <li class="menu-item">
        <a href="/" class="menu-link">
          <i class="bi bi-grid-fill"></i>
          <span>Home</span>
        </a>
      </li>
      <li class="menu-item">
        <a href="/portfolio" class="menu-link">
          <i class="bi bi-people-fill"></i>
          <span>Developer Team</span>
        </a>
      </li>
    </ul>
  </div>
</nav>
</header>
`
document.getElementById('main').prepend(template.content.cloneNode(true))




