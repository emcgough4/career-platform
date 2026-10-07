-- Portfolio work, added 2026-10-07 from the 2026 portfolio PDF, the owner's Instagram/YouTube links and XDR links.
-- Likes and views are as shown on Instagram or in the portfolio PDF on 2026-10-07.
-- Run once: sqlite3 data/career_platform.db < scripts/add_portfolio_projects.sql
-- Explicit ids make a second run fail instead of duplicating rows.
PRAGMA foreign_keys = ON;
BEGIN;

INSERT INTO projects (id, profile_id, title, short_description, long_description, approach, outcome, metrics, status, featured, cover_image_url, project_url, year) VALUES
(1, 1, 'Stop Sign Patrol',
 'Do LMU students actually stop at stop signs? A street-comedy reel for The Loyolan.',
 'AE intern Jonah Kessler-Cohen patrolled an on-campus stop sign to see how many drivers would roll through it. A simple, relatable premise built for the first second of the scroll.',
 'Shot and edited by me as AE producer, with Jack Kenneally (asst. AE producer) and Jonah Kessler-Cohen (AE intern).',
 NULL,
 '17.6K views · 550 likes', 'published', 1, '/static/media/work/stop-sign-patrol.jpg', 'https://www.instagram.com/reel/DR0Tqkwkyex/', 2025),
(2, 1, 'Fallapalooza × Charlie & Lola',
 'Our take on the viral "Charlie and Lola" trend at LMU''s fall music festival.',
 'LMU students flaunted their Fallapalooza style on Sunken Gardens. I photographed them at the festival, and the Loyolan''s cartoon team turned the photos into "Charlie & Lola" characters for the reel.',
 'Shot and edited by me as AE producer, with Jack Kenneally (asst. AE producer). Cartoons by Ren Martino, Amelie Stein and Michaela Gabriel.',
 NULL,
 '7,809 views · 298 likes', 'published', 1, '/static/media/work/fallapalooza-charlie-and-lola.jpg', 'https://www.instagram.com/reel/DPjymlFioI-/', 2025),
(3, 1, 'What''s Up Wednesdays',
 'My weekly on-camera street-interview series for The Loyolan.',
 'Each week I host What''s Up Wednesdays, asking students about campus life and the greater LA community. In this episode: what song reminds you of your experience at LMU?',
 'Hosted, shot and edited by me as AE producer, with Jagger Ong Patzwald and Maria Cranston (asst. AE producers) and AE interns Ella Perius, Ava Reid and Jack Kenneally.',
 NULL,
 '9,722 views · 245 likes', 'published', 1, '/static/media/work/whats-up-wednesdays-song.jpg', 'https://www.instagram.com/reel/DPW6kuOFQ5d/', 2025),
(4, 1, 'Beyond the Newsroom',
 'A video format I created that became a weekly Loyolan feature.',
 'Beyond the Newsroom takes the AE team out to campus events to try everything on camera. In this episode, ASLMU''s annual Christmas Tree Lighting on Alumni Mall: sledding, holiday treats and much more.',
 'I created the format, then shot and edited this episode as AE producer with the AE team.',
 'Became a recurring weekly series.',
 '147 likes', 'published', 1, '/static/media/work/beyond-the-newsroom-tree-lighting.jpg', 'https://www.instagram.com/reel/DSdgX7Zj2R8/', 2025),
(5, 1, 'XDR Radiology Demo Short',
 'A product-marketing YouTube Short inviting dental practices to book a free demo.',
 'Short-form product marketing video created for XDR Radiology''s YouTube channel: "See Our Dental Imaging Solutions in Action."',
 NULL, NULL,
 NULL, 'published', 1, '/static/media/work/xdr-demo-short.jpg', 'https://www.youtube.com/shorts/WCwzS8pMXdE', 2026),
(6, 1, 'Wellness Wednesday XXL',
 'The AE team tries everything at LMU''s first Wellness Wednesday XXL.',
 'Student Affairs, Student EXP, LMU CARES and others hosted Wellness Wednesday XXL to celebrate the end of the semester. From inflatable obstacle courses to relaxing massages, our AE team explored everything on offer.',
 'Shot and edited by me as AE producer, with Jagger Ong Patzwald and Maria Cranston (asst. AE producers) and AE interns Ella Perius, Ava Reid and Jack Kenneally.',
 NULL,
 '320 likes', 'published', 0, '/static/media/work/wellness-wednesday-xxl.jpg', 'https://www.instagram.com/reel/DJaeHi4vswP/', 2025),
(7, 1, 'The Student Private Investigator',
 'Film student by day, private investigator by night: a side-hustle profile.',
 'While others pursue internships or on-campus jobs, Zachary LaBeaux took an unconventional side hustle. A short profile built around one surprising hook.',
 'Shot and edited by me as AE producer, with Athena Cheris (enterprise reporter).',
 NULL,
 '301 likes', 'published', 0, '/static/media/work/side-hustle-private-investigator.jpg', 'https://www.instagram.com/reel/DRajsR3jnp-/', 2025),
(8, 1, 'Is Imaging Fatigue Affecting Your Practice?',
 'An SEO-focused blog post for XDR Radiology''s dental audience.',
 'Educational long-form content for dental professionals on minimizing retakes, improving imaging workflows and supporting more efficient imaging, written to strengthen XDR''s organic search presence.',
 NULL, NULL,
 NULL, 'published', 0, '/static/media/work/xdr-imaging-fatigue-blog.jpg', 'https://xdrradiology.com/imaging-fatigue/', 2026),
(9, 1, 'XDR Radiology Press Kit',
 'Official brand and media resources for XDR Radiology.',
 'A press kit packaging XDR Radiology''s official brand and media resources for journalists and partners.',
 NULL, NULL,
 NULL, 'published', 0, '/static/media/work/xdr-press-kit.jpg', 'https://drive.google.com/file/d/1-2tOhSzje9WFtMRv7XTev7uNbwf7i2_z/view', 2026),
(10, 1, 'Loyolan Social Strategy',
 'Leading The Loyolan''s social channels across five platforms.',
 'As Audience Engagement Producer I lead a team managing Instagram, TikTok, YouTube, X and Facebook, using SocialPilot to schedule content and find the best posting times. I produce and edit short-form video with graphics, host weekly series such as What''s Up Wednesdays and Beyond the Newsroom, and manage the Instagram link-in-bio so the day''s stories are one tap away.',
 NULL, NULL,
 '@laloyolan · 10K followers', 'published', 0, '/static/media/work/loyolan-social-strategy.jpg', 'https://www.instagram.com/laloyolan/', 2025),
(11, 1, 'Dollars + Sense',
 'A gamified financial-literacy web app built for the M-School program.',
 'In M-School, my team developed and marketed a product: a web app that builds financial literacy among college students through game-like elements and streak incentives built around real-life scenarios.',
 'I led the website development, designing and building the app independently with Base44, an AI app builder.',
 NULL,
 NULL, 'published', 0, '/static/media/work/dollars-and-sense-web-app.jpg', 'https://dollars-sense-a985a1e8.base44.app/dashboard', 2025),
(12, 1, 'DRM Engineering Website Redesign',
 'Redesigning a structural engineering firm''s website in WordPress.',
 'I am redesigning the website for DRM Engineering. I have established the overall layout, page structure and navigation, updated the design to better reflect the brand''s logo, and am building a project portfolio section. Current site: drmengineering.com.',
 NULL, NULL,
 NULL, 'published', 0, '/static/media/work/drm-engineering-redesign.jpg', 'https://wordpress-668715-5690855.cloudwaysapps.com/', 2026),
(13, 1, 'Spider Creations Web Management',
 'WordPress content management for small-business client sites.',
 'As a Website Development Intern at Spider Creations, I trained in WordPress and Beaver Builder. I managed weekly news blog posts for Zero Emission Trucking Washington (scheduling, headlines and taglines) and kept client sites current, such as adding staff profiles to Aquaventure Scuba''s "Meet the Staff" page.',
 NULL, NULL,
 NULL, 'published', 0, '/static/media/work/spider-creations-web-management.jpg', 'https://spidercreations.net/', 2025);

INSERT OR IGNORE INTO tags (label) VALUES
('Instagram Reels'), ('Short-form video'), ('On-camera host'), ('Series format'), ('YouTube Shorts'),
('Product marketing'), ('SEO'), ('Copywriting'), ('Brand'), ('Social strategy'), ('Web design'), ('WordPress'), ('Web app');

INSERT INTO project_tags (project_id, tag_id)
SELECT p, (SELECT id FROM tags WHERE label = t) FROM (
  SELECT 1 AS p, 'Instagram Reels' AS t UNION ALL SELECT 1, 'Short-form video'
  UNION ALL SELECT 2, 'Instagram Reels' UNION ALL SELECT 2, 'Short-form video'
  UNION ALL SELECT 3, 'Instagram Reels' UNION ALL SELECT 3, 'On-camera host' UNION ALL SELECT 3, 'Series format'
  UNION ALL SELECT 4, 'Instagram Reels' UNION ALL SELECT 4, 'Series format'
  UNION ALL SELECT 5, 'YouTube Shorts' UNION ALL SELECT 5, 'Product marketing'
  UNION ALL SELECT 6, 'Instagram Reels' UNION ALL SELECT 6, 'Short-form video'
  UNION ALL SELECT 7, 'Instagram Reels' UNION ALL SELECT 7, 'Short-form video'
  UNION ALL SELECT 8, 'SEO' UNION ALL SELECT 8, 'Copywriting'
  UNION ALL SELECT 9, 'Brand' UNION ALL SELECT 9, 'Product marketing'
  UNION ALL SELECT 10, 'Social strategy' UNION ALL SELECT 10, 'Short-form video'
  UNION ALL SELECT 11, 'Web app' UNION ALL SELECT 11, 'Web design'
  UNION ALL SELECT 12, 'Web design' UNION ALL SELECT 12, 'WordPress'
  UNION ALL SELECT 13, 'WordPress' UNION ALL SELECT 13, 'Copywriting'
);

-- Headshot for the home page hero (cropped to 9:16, metadata stripped).
UPDATE profiles SET photo_url = '/static/media/eleanor-mcgough.jpg' WHERE id = 1;

COMMIT;
