<template>
  <div class="home">
    <div class="hero">
      <h1>🎟️ Welcome to Coupon Service</h1>
      <p>Manage and redeem your coupons with ease</p>
      <div class="cta-buttons">
        <router-link to="/login" class="btn btn-primary">Get Started</router-link>
        <router-link to="/register" class="btn btn-secondary">Create Account</router-link>
      </div>
    </div>

    <div class="features">
      <div class="feature-card">
        <div class="icon">📚</div>
        <h3>Coupon Books</h3>
        <p>Organize coupons into books for easy management</p>
      </div>
      <div class="feature-card">
        <div class="icon">🎯</div>
        <h3>Easy Redemption</h3>
        <p>Redeem coupons with a simple code</p>
      </div>
      <div class="feature-card">
        <div class="icon">👥</div>
        <h3>User Management</h3>
        <p>Admin tools for managing users and coupons</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Home page component
</script>

<style scoped>
.home {
  text-align: center;
}

.hero {
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-block;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 2rem 0;
}

.feature-card {
  padding: 2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: #6c757d;
}
</style>
