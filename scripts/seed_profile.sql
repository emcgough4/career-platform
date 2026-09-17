PRAGMA foreign_keys = ON;

INSERT INTO profiles (id, full_name, headline, summary, location, email, linkedin_url)
VALUES (1, 'Your Name', 'Creative and strategic marketing designer',
        'A concise professional summary belongs here.', 'Your Location',
        'you@example.com', 'https://www.linkedin.com/in/your-profile');

INSERT INTO skills (profile_id, name, category, sort_order)
VALUES (1, 'Brand strategy', 'Strategy', 1),
       (1, 'Visual design', 'Design', 2),
       (1, 'Marketing', 'Marketing', 3);
