# Database Population Commands

This document describes the Django management commands available for populating your CoFound database with realistic sample data for development and testing purposes.

## 🚀 Quick Start

To populate your database with all sample data at once, run:

```bash
python manage.py populate_all_data
```

This will create:
- 10 entrepreneur users with profiles and startups
- 10 investor users with profiles and portfolios
- Posts, comments, likes, and saved posts
- Funding rounds and investment commitments
- User connections (follows) and collaboration requests
- Meetings between entrepreneurs and investors
- Messages between users
- Notifications and activity logs

## 📋 Available Commands

### 1. Create Users

#### Create Entrepreneurs
```bash
python manage.py create_entrepreneurs
```
Creates 10 entrepreneur users with:
- Email: entrepreneur1@gmail.com to entrepreneur10@gmail.com
- Password: cofound27
- Realistic profiles with company names, bios, and startup details
- Startups with descriptions and sample documents

#### Create Investors
```bash
python manage.py create_investors
```
Creates 10 investor users with:
- Email: investor1@gmail.com to investor10@gmail.com
- Password: cofound27
- Realistic profiles with firm names, investment preferences, and portfolios
- Investment documents and portfolio summaries

### 2. Create Content

#### Populate Posts and Social Activity
```bash
python manage.py populate_posts
```
Creates:
- 5 posts per user with realistic content
- Random likes and saves on posts
- Comments from other users
- Occasional media attachments

#### Populate Funding Rounds
```bash
python manage.py populate_funding_rounds
```
Creates:
- 1-3 funding rounds per startup
- Investment commitments from random investors
- Realistic funding goals and equity offerings
- Various statuses (active, successful, failed)

### 3. Create Connections

#### Populate Connections and Collaboration
```bash
python manage.py populate_connections
```
Creates:
- Realistic follow relationships between users
- Collaboration requests from investors to entrepreneurs
- Various request statuses (pending, accepted, rejected)

#### Populate Meetings
```bash
python manage.py populate_meetings
```
Creates:
- Meetings between entrepreneurs and investors
- Various meeting types (in-person, video call, phone call)
- Realistic meeting schedules and locations
- Different meeting statuses

### 4. Create Communication

#### Populate Messages
```bash
python manage.py populate_messages
```
Creates:
- Realistic conversations between users
- Role-appropriate message content
- Follow-up messages and general conversation
- Various read/unread statuses

#### Populate Notifications and Activity Logs
```bash
python manage.py populate_notifications
```
Creates:
- Notifications for various user activities
- Activity logs tracking user actions
- Realistic notification content and timing

## 🎯 Master Command

### Populate All Data
```bash
python manage.py populate_all_data
```

This command runs all the above commands in the correct order and provides comprehensive statistics.

#### Command Options

You can skip specific steps using flags:

```bash
# Skip user creation (use existing users)
python manage.py populate_all_data --skip-users

# Skip post creation
python manage.py populate_all_data --skip-posts

# Skip funding rounds
python manage.py populate_all_data --skip-funding

# Skip connections
python manage.py populate_all_data --skip-connections

# Skip meetings
python manage.py populate_all_data --skip-meetings

# Skip messages
python manage.py populate_all_data --skip-messages

# Skip notifications
python manage.py populate_all_data --skip-notifications

# Combine multiple skips
python manage.py populate_all_data --skip-users --skip-posts
```

## 🔑 Login Credentials

After running the commands, you can log in with:

### Entrepreneurs
- **Email**: entrepreneur1@gmail.com to entrepreneur10@gmail.com
- **Password**: cofound27

### Investors
- **Email**: investor1@gmail.com to investor10@gmail.com
- **Password**: cofound27

## 📊 Expected Data Volume

When you run all commands, expect to see approximately:

- **Users**: 20 total (10 entrepreneurs + 10 investors)
- **Startups**: 10 (1 per entrepreneur)
- **Posts**: 100 (5 per user)
- **Comments**: 200-400 (2-4 per post)
- **Funding Rounds**: 15-30 (1-3 per startup)
- **Investment Commitments**: 30-80 (2-8 per funding round)
- **Favorites**: 60-120 (3-6 per user)
- **Collaboration Requests**: 20-40 (2-4 per investor)
- **Meetings**: 40-80 (2-4 per user pair)
- **Messages**: 100-200 (5-10 per user pair)
- **Notifications**: 100-300 (5-15 per user)
- **Activity Logs**: 160-400 (8-20 per user)

## ⚠️ Important Notes

### Idempotent Operations
All commands are designed to be safe to run multiple times:
- Existing users won't be duplicated
- Existing content won't be overwritten
- Commands will skip already-created data

### Database Requirements
Ensure your database is properly migrated before running:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Performance Considerations
- Commands use bulk operations where possible
- Large datasets may take several minutes to create
- Consider running during off-peak hours for production-like environments

### Customization
You can modify the sample data in each command file to:
- Change company names and descriptions
- Adjust the number of items created per user
- Modify message content and timing
- Customize industry preferences and locations

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all required models are properly imported
2. **Database Constraints**: Check that your database schema matches the models
3. **Memory Issues**: For very large datasets, consider running commands individually

### Debug Mode
Run commands with increased verbosity for debugging:
```bash
python manage.py populate_all_data --verbosity=2
```

### Partial Population
If you encounter issues, you can run commands individually to isolate problems:
```bash
python manage.py create_entrepreneurs
python manage.py create_investors
# ... then continue with other commands
```

## 🔄 Re-running Commands

To refresh your sample data:

1. **Clear existing data** (if needed):
   ```bash
   python manage.py flush  # WARNING: This clears ALL data
   ```

2. **Re-run population commands**:
   ```bash
   python manage.py populate_all_data
   ```

## 📈 Monitoring Progress

Each command provides progress updates and final statistics. The master command (`populate_all_data`) gives you a comprehensive overview of all created data.

## 🎉 Success Indicators

When successful, you should see:
- ✅ Success messages for each step
- 📊 Comprehensive statistics at the end
- 🔑 Login credentials reminder
- 🎯 Realistic data that makes your application feel alive

Your CoFound application is now populated with realistic sample data and ready for development, testing, and demonstration purposes!
