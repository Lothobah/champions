# Generated by Django 5.0.4 on 2024-07-23 21:09

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Academic_Year',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('academic_year', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('semester', models.CharField(choices=[('First Term', 'First Term'), ('Second Term', 'Second Term'), ('Third Term', 'Third Term')], default='First Term', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[(1, 'HOD'), (2, 'Staff'), (3, 'Student'), (4, 'Bursar')], default=1, max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AdminHOD',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bursar',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone_number', models.TextField()),
                ('gender', models.CharField(max_length=10)),
                ('date_of_birth', models.DateField()),
                ('firebase_token', models.TextField(default='')),
                ('address1', models.TextField(blank=True, null=True)),
                ('address2', models.TextField()),
                ('staff_profile_pic', models.FileField(upload_to='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=255)),
                ('course_code', models.CharField(max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('staff_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default='', max_length=1000)),
                ('file', models.FileField(default='', upload_to='')),
                ('post_time', models.CharField(max_length=100)),
                ('deadline', models.CharField(max_length=100)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.courses')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500)),
                ('time', models.CharField(max_length=100)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.courses')),
            ],
        ),
        migrations.CreateModel(
            name='Programmes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('programme_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('staff_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resources',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_resource', models.FileField(default='', upload_to='')),
                ('title', models.CharField(max_length=100)),
                ('course', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.courses')),
            ],
        ),
        migrations.CreateModel(
            name='Staffs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone_number', models.TextField()),
                ('gender', models.CharField(max_length=10)),
                ('date_of_birth', models.DateField()),
                ('firebase_token', models.TextField(default='')),
                ('address1', models.TextField()),
                ('address2', models.TextField()),
                ('staff_profile_pic', models.FileField(upload_to='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StaffNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('staff_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.staffs')),
            ],
        ),
        migrations.CreateModel(
            name='StaffLeaveReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('leave_date', models.CharField(max_length=255)),
                ('leave_message', models.TextField()),
                ('leave_status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('staff_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.staffs')),
            ],
        ),
        migrations.CreateModel(
            name='StudentLevel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level_name', models.CharField(max_length=25)),
                ('staff_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OnlineClassRoom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('room_name', models.CharField(max_length=255)),
                ('room_pwd', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.courses')),
                ('started_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.staffs')),
                ('student_level_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.studentlevel')),
            ],
        ),
        migrations.AddField(
            model_name='courses',
            name='student_level_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.studentlevel'),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('attendance_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('academic_year_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.academic_year')),
                ('semester_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.semester')),
                ('student_level_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.studentlevel')),
            ],
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('gender', models.CharField(max_length=10)),
                ('date_of_birth', models.DateField()),
                ('profile_pic', models.FileField(upload_to='')),
                ('home_town', models.TextField()),
                ('parent_name', models.CharField(max_length=255)),
                ('parent_phone', models.TextField()),
                ('firebase_token', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('courses', models.ManyToManyField(related_name='students', to='great_alliance_portal.courses')),
                ('student_level_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.studentlevel')),
            ],
        ),
        migrations.CreateModel(
            name='StudentResults',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('individual_test_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('group_work_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('class_test_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('project_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assignment_mark', models.DecimalField(decimal_places=2, max_digits=5)),
                ('exam_mark', models.DecimalField(decimal_places=2, max_digits=5)),
                ('total_mark', models.DecimalField(decimal_places=2, max_digits=5)),
                ('overral_mark', models.DecimalField(decimal_places=2, max_digits=5)),
                ('aggregate', models.CharField(max_length=2)),
                ('overral_mark_average', models.DecimalField(decimal_places=2, max_digits=5)),
                ('grade', models.CharField(max_length=50)),
                ('remark', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('academic_year_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.academic_year')),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.courses')),
                ('semester_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.semester')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.students')),
            ],
        ),
        migrations.CreateModel(
            name='StudentNotification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.students')),
            ],
        ),
        migrations.CreateModel(
            name='StudentLeaveReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('leave_date', models.CharField(max_length=255)),
                ('leave_message', models.TextField()),
                ('leave_status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.students')),
            ],
        ),
        migrations.CreateModel(
            name='Fees',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('arrears_from_last_term', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('school_fees', models.DecimalField(decimal_places=2, max_digits=20)),
                ('extra_classes', models.DecimalField(decimal_places=2, max_digits=20)),
                ('stationary', models.DecimalField(decimal_places=2, max_digits=20)),
                ('sport_culture', models.DecimalField(decimal_places=2, max_digits=20)),
                ('ict', models.DecimalField(decimal_places=2, max_digits=20)),
                ('pta', models.DecimalField(decimal_places=2, max_digits=20)),
                ('maintenance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('light_bill', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_fees', models.DecimalField(decimal_places=2, max_digits=20)),
                ('overall_fees', models.DecimalField(decimal_places=2, max_digits=25)),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('student_level_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.studentlevel')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.students')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('attendance_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='great_alliance_portal.attendance')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='great_alliance_portal.students')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_submitted', models.FileField(default='', upload_to='')),
                ('time_submitted', models.CharField(max_length=100)),
                ('assignment', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='great_alliance_portal.assignment')),
                ('user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
