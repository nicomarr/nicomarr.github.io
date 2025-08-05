---
layout: page
title: Contact
permalink: /contact/
---

<form id="contact-form" action="https://formsubmit.co/7e3f0d4545fcdf7f7ce70ba4ca1f9576" method="POST">
  <!-- FormSubmit settings -->
  <input type="hidden" name="_subject" value="New contact form submission">
  <input type="hidden" name="_next" value="{{ site.url }}{{ site.baseurl }}/thanks">
  <input type="hidden" name="_captcha" value="false">
  <input type="text" name="_honey" style="display:none">
  
  <div class="form-field">
    <label for="name">Name *</label>
    <input type="text" id="name" name="name" required>
    <span class="error" id="name-error"></span>
  </div>
  
  <div class="form-field">
    <label for="email">Email *</label>
    <input type="email" id="email" name="email" required>
    <span class="error" id="email-error"></span>
  </div>
  
  <div class="form-field">
    <label for="message">Message *</label>
    <textarea id="message" name="message" rows="5" required></textarea>
    <span class="error" id="message-error"></span>
  </div>
  
  <button type="submit" id="submit-btn">Send Message</button>
</form>

<style>
.form-field {
  margin-bottom: 1.5em;
}

.form-field label {
  display: block;
  margin-bottom: 0.3em;
  font-weight: 600;
}

.form-field input,
.form-field textarea {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 16px;
}

.form-field input:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #2a7ae4;
}

.error {
  color: #dc2626;
  font-size: 0.875em;
  display: block;
  margin-top: 0.25em;
}

#submit-btn {
  background: #2a7ae4;
  color: white;
  border: none;
  padding: 0.75em 2em;
  border-radius: 3px;
  cursor: pointer;
  font-size: 16px;
}

#submit-btn:hover {
  background: #1756a9;
}

#submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>

<script>
document.getElementById('contact-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  // Clear errors
  document.querySelectorAll('.error').forEach(el => el.textContent = '');
  
  // Validate
  let valid = true;
  
  const name = document.getElementById('name');
  if (name.value.trim().length < 2) {
    document.getElementById('name-error').textContent = 'Name must be at least 2 characters';
    valid = false;
  }
  
  const email = document.getElementById('email');
  if (!email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
    document.getElementById('email-error').textContent = 'Please enter a valid email';
    valid = false;
  }
  
  const message = document.getElementById('message');
  if (message.value.trim().length < 10) {
    document.getElementById('message-error').textContent = 'Message must be at least 10 characters';
    valid = false;
  }
  
  if (valid) {
    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.textContent = 'Sending...';
    this.submit();
  }
});
</script>