import random
from datetime import date, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.conf import settings
from apps.accounts.models import User
from apps.customers.models import Customer
from apps.projects.models import Project, ProjectPhase, Amenity
from apps.plots.models import Plot, PlotImage
from apps.sales.models import Sale, InstallmentSchedule
from apps.payments.models import Payment
from apps.documents.models import Document
from apps.notifications.models import Notification
from apps.settings.models import CompanySetting


class Command(BaseCommand):
    help = 'Seed the database with test data including images from landImage folder'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # --- Copy images from landImage/ to media/ ---
        import shutil
        src_dir = settings.BASE_DIR / 'landImage'
        media_plots = settings.BASE_DIR / 'media' / 'plots'
        media_projects = settings.BASE_DIR / 'media' / 'projects'
        media_plots.mkdir(parents=True, exist_ok=True)
        media_projects.mkdir(parents=True, exist_ok=True)
        if src_dir.exists():
            for f in src_dir.iterdir():
                if f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                    dest = media_plots / f.name
                    if not dest.exists():
                        shutil.copy2(f, dest)
                    dest2 = media_projects / f.name
                    if not dest2.exists():
                        shutil.copy2(f, dest2)
            self.stdout.write(f'  Copied images from landImage/ to media/')
        else:
            self.stdout.write('  landImage/ not found, skipping image copy')

        # --- Company Setting ---
        CompanySetting.objects.get_or_create(
            company_name='Prime Lands Ltd',
            defaults={
                'tagline': 'Your Trusted Real Estate Partner',
                'email': 'info@primelands.co.ke',
                'phone': '+254 712 345 678',
                'address': 'Prime Tower, Upper Hill, Nairobi',
            }
        )

        # --- Amenities ---
        amenity_names = [
            ('Water Supply', 'water'),
            ('Electricity', 'zap'),
            ('Road Access', 'map'),
            ('School', 'book'),
            ('Hospital', 'plus-circle'),
            ('Shopping Center', 'shopping-bag'),
            ('Police Station', 'shield'),
            ('Bank', 'dollar-sign'),
            ('Place of Worship', 'heart'),
            ('Park', 'wind'),
        ]
        amenities = {}
        for name, icon in amenity_names:
            amenity, _ = Amenity.objects.get_or_create(name=name, defaults={'icon': icon})
            amenities[name] = amenity
        self.stdout.write('  Created amenities')

        # --- Staff Users ---
        staff_users = {}
        staff_data = [
            ('admin', 'admin@primelands.co.ke', 'Admin', 'User', 'administrator'),
            ('finance', 'finance@primelands.co.ke', 'Grace', 'Finance', 'finance_officer'),
            ('sales', 'sales@primelands.co.ke', 'Peter', 'Sales', 'sales_agent'),
        ]
        for username, email, first, last, role in staff_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'is_staff': True,
                    'password': make_password('admin123'),
                }
            )
            if created:
                user.password = make_password('admin123')
                user.save()
            staff_users[role] = user
        self.stdout.write('  Created staff users (password: admin123)')

        # --- Customer Users ---
        customer_users = []
        customer_data = [
            ('john', 'john@email.com', 'John', 'Mwangi', '0712345678', 'customer'),
            ('jane', 'jane@email.com', 'Jane', 'Wanjiku', '0723456789', 'customer'),
            ('peter', 'peter@email.com', 'Peter', 'Kamau', '0734567890', 'customer'),
        ]
        for username, email, first, last, phone, role in customer_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'phone': phone,
                    'password': make_password('customer123'),
                }
            )
            if created:
                user.password = make_password('customer123')
                user.save()
            customer_users.append(user)
        self.stdout.write('  Created customer users (password: customer123)')

        # --- Customer Profiles ---
        customers = []
        for i, user in enumerate(customer_users):
            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'national_id': ['12345678', '87654321', '56781234'][i],
                    'phone': user.phone,
                    'city': ['Nairobi', 'Nairobi', 'Kiambu'][i],
                    'address': ['123 Green Kenya Avenue', '456 Valley Road', '789 Ridge Lane'][i],
                    'is_verified': True,
                }
            )
            customers.append(customer)
        self.stdout.write('  Created customer profiles')

        # --- Projects ---
        project_data = [
            {
                'name': 'Green Valley Estate',
                'location': 'Kiambu Road, Nairobi',
                'description': 'A serene residential estate surrounded by lush greenery. Green Valley offers spacious plots perfect for building your dream home. Located along Kiambu Road with easy access to Nairobi CBD, this estate features well-planned infrastructure including tarmac roads, street lighting, and underground utilities.',
                'total_plots': 45,
                'status': 'active',
                'featured': True,
                'coordinates': '-1.1987,36.8562',
                'start_date': '2025-01-15',
                'image': 'projects/land1.jpg',
            },
            {
                'name': 'Sunset Ridge',
                'location': 'Ngong Road, Nairobi',
                'description': 'Premium residential plots with breathtaking sunset views over the Ngong Hills. Sunset Ridge combines luxury living with natural beauty. Each plot offers panoramic views and the estate comes with modern amenities including a clubhouse, swimming pool, and landscaped gardens.',
                'total_plots': 30,
                'status': 'active',
                'featured': True,
                'coordinates': '-1.3619,36.6826',
                'start_date': '2025-03-01',
                'image': 'projects/land2.jpg',
            },
            {
                'name': 'Lakeview Heights',
                'location': 'Ruiru, Kiambu County',
                'description': 'An upcoming residential development near scenic lake views. Lakeview Heights offers affordable plots in a rapidly developing area with great potential for value appreciation. Close to major schools, shopping centers, and with excellent road connectivity.',
                'total_plots': 25,
                'status': 'coming_soon',
                'featured': False,
                'coordinates': '-1.1433,36.9642',
                'start_date': '2025-07-01',
                'image': 'projects/land3.jpg',
            },
        ]

        projects = []
        for i, pd in enumerate(project_data):
            project, _ = Project.objects.get_or_create(
                name=pd['name'],
                defaults={
                    'location': pd['location'],
                    'description': pd['description'],
                    'total_plots': pd['total_plots'],
                    'status': pd['status'],
                    'featured': pd['featured'],
                    'coordinates': pd['coordinates'],
                    'start_date': pd['start_date'],
                    'image': pd['image'],
                }
            )
            projects.append(project)
        self.stdout.write('  Created projects')

        # --- ProjectPhases ---
        phase_data = [
            (projects[0], 'Phase 1', 1, 15),
            (projects[0], 'Phase 2', 2, 20),
            (projects[0], 'Phase 3', 3, 10),
            (projects[1], 'Phase 1', 1, 15),
            (projects[1], 'Phase 2', 2, 15),
            (projects[2], 'Phase 1', 1, 25),
        ]
        phases = []
        for project, name, order, total in phase_data:
            phase, _ = ProjectPhase.objects.get_or_create(
                project=project,
                name=name,
                defaults={'order': order, 'total_plots': total}
            )
            phases.append(phase)
        self.stdout.write('  Created project phases')

        # --- Plots ---
        status_choices = ['available', 'available', 'available', 'reserved', 'sold', 'blocked']
        plot_count = 0

        # Green Valley plots
        gv_phases = [p for p in phases if p.project == projects[0]]
        for phase in gv_phases:
            for j in range(1, phase.total_plots + 1):
                size = round(random.uniform(0.05, 0.25), 2)
                price = round(random.uniform(3000000, 8000000), -3)
                Plot.objects.get_or_create(
                    project=projects[0],
                    plot_number=f'GV-{phase.order:02d}-{j:03d}',
                    defaults={
                        'phase': phase,
                        'size_sqm': size * 4046.86,
                        'price': price,
                        'deposit_percentage': 20,
                        'max_installment_months': 60,
                        'interest_rate': random.choice([0, 5, 8]),
                        'status': random.choice(status_choices),
                        'description': f'Beautiful plot in Green Valley Estate, Phase {phase.order}. Ideal for residential development.',
                        'coordinates': f'-1.19{random.randint(80, 99)},{36.85}{random.randint(50, 99)}',
                        'featured': random.choice([True, False]),
                    }
                )
                plot_count += 1

        # Sunset Ridge plots
        sr_phases = [p for p in phases if p.project == projects[1]]
        for phase in sr_phases:
            for j in range(1, phase.total_plots + 1):
                size = round(random.uniform(0.08, 0.3), 2)
                price = round(random.uniform(5000000, 12000000), -3)
                Plot.objects.get_or_create(
                    project=projects[1],
                    plot_number=f'SR-{phase.order:02d}-{j:03d}',
                    defaults={
                        'phase': phase,
                        'size_sqm': size * 4046.86,
                        'price': price,
                        'deposit_percentage': 25,
                        'max_installment_months': 48,
                        'interest_rate': random.choice([0, 5]),
                        'status': random.choice(status_choices),
                        'description': f'Premium plot in Sunset Ridge. Enjoy stunning views of Ngong Hills.',
                        'coordinates': f'-1.36{random.randint(10, 30)},{36.68}{random.randint(10, 40)}',
                        'featured': random.choice([True, False]),
                    }
                )
                plot_count += 1

        # Lakeview Heights plots
        lv_phases = [p for p in phases if p.project == projects[2]]
        for phase in lv_phases:
            for j in range(1, phase.total_plots + 1):
                size = round(random.uniform(0.04, 0.15), 2)
                price = round(random.uniform(1800000, 4500000), -3)
                Plot.objects.get_or_create(
                    project=projects[2],
                    plot_number=f'LV-{phase.order:02d}-{j:03d}',
                    defaults={
                        'phase': phase,
                        'size_sqm': size * 4046.86,
                        'price': price,
                        'deposit_percentage': 15,
                        'max_installment_months': 72,
                        'interest_rate': 10,
                        'status': 'available',
                        'description': f'Affordable plot in Lakeview Heights. Great investment opportunity.',
                        'coordinates': f'-1.14{random.randint(20, 50)},{36.96}{random.randint(20, 50)}',
                        'featured': False,
                    }
                )
                plot_count += 1

        self.stdout.write(f'  Created {plot_count} plots')

        # --- Assign amenities to some plots ---
        all_plots = list(Plot.objects.all())
        for plot in all_plots:
            num_amenities = random.randint(3, 6)
            selected = random.sample(list(amenities.values()), num_amenities)
            plot.amenities.add(*selected)
        self.stdout.write('  Assigned amenities to plots')

        # --- Create a Sale for John Mwangi ---
        available_plots = list(Plot.objects.filter(status='available'))
        if available_plots:
            sold_plot = available_plots[0]
            sold_plot.status = 'sold'
            saved_plot = sold_plot.save()

            sale, created = Sale.objects.get_or_create(
                customer=customers[0],
                plot=sold_plot,
                defaults={
                    'sales_agent': staff_users['sales_agent'],
                    'status': 'active',
                    'selling_price': sold_plot.price,
                    'deposit_amount': sold_plot.deposit_amount,
                    'deposit_paid': True,
                    'installment_months': 36,
                    'monthly_installment': sold_plot.monthly_installment(36),
                    'interest_rate': sold_plot.interest_rate,
                    'notes': 'Initial purchase agreement signed.',
                }
            )

            if created:
                # Create installment schedule
                monthly = sold_plot.monthly_installment(36)
                for i in range(36):
                    due = date.today() + timedelta(days=30 * (i + 1))
                    InstallmentSchedule.objects.create(
                        sale=sale,
                        installment_number=i + 1,
                        due_date=due,
                        amount=monthly,
                    )

                # Create deposit payment
                Payment.objects.create(
                    sale=sale,
                    customer=customers[0],
                    amount=sold_plot.deposit_amount,
                    payment_method='bank',
                    transaction_code='BANK-TXN-001',
                    status='confirmed',
                    payment_date=date.today() - timedelta(days=60),
                    confirmed_by=staff_users['finance_officer'],
                )

                # Create 3 monthly payments
                for month in range(1, 4):
                    Payment.objects.create(
                        sale=sale,
                        customer=customers[0],
                        amount=monthly,
                        payment_method=random.choice(['bank', 'cash', 'mpesa']),
                        transaction_code=f'TXN-{month:04d}',
                        status='confirmed',
                        payment_date=date.today() - timedelta(days=30 * (4 - month)),
                    confirmed_by=staff_users['finance_officer'],
                    )

                # Mark first 3 installments as paid
                for i in range(3):
                    inst = InstallmentSchedule.objects.filter(sale=sale, installment_number=i + 1).first()
                    if inst:
                        inst.paid = True
                        inst.paid_date = date.today() - timedelta(days=30 * (3 - i))
                        inst.save()

            self.stdout.write('  Created sale with payments and installments')

        # --- Create Documents for customers with sales ---
        from apps.documents.models import Document
        doc_customers = [(customers[0], 'John Mwangi'), (customers[2], 'Peter Kamau')]
        all_docs_data = [
            ('sale_agreement', 'Sale Agreement', 'Signed sale agreement for the plot'),
            ('survey_map', 'Survey Map', 'Official survey map for the plot'),
            ('receipt', 'Deposit Payment Receipt', 'Deposit payment receipt for the plot'),
            ('receipt', 'Monthly Payment Receipt 1', 'First monthly installment receipt'),
            ('receipt', 'Monthly Payment Receipt 2', 'Second monthly installment receipt'),
            ('beacon_certificate', 'Beacon Certificate', 'Beacon certificate for plot boundaries'),
        ]
        total_docs = 0
        for cust, name in doc_customers:
            created = 0
            for doc_type, title, desc in all_docs_data:
                doc, was_created = Document.objects.get_or_create(
                    customer=cust,
                    title=f'{title} - {name}',
                    defaults={
                        'document_type': doc_type,
                        'description': desc,
                        'file': 'documents/sample.pdf',
                        'uploaded_by': staff_users['administrator'],
                    }
                )
                if was_created:
                    created += 1
            total_docs += created
            self.stdout.write(f'  Created {created} documents for {name}')
        self.stdout.write(f'  Total documents created: {total_docs}')

        # --- Create a Reservation for Jane ---
        reserved_plot = list(Plot.objects.filter(status='available'))
        if reserved_plot:
            from apps.sales.models import Reservation
            plot_to_reserve = reserved_plot[0]
            plot_to_reserve.status = 'reserved'
            plot_to_reserve.save()

            Reservation.objects.get_or_create(
                customer=customers[1],
                plot=plot_to_reserve,
                defaults={
                    'reserved_by': staff_users['sales_agent'],
                    'expiry_date': timezone.now() + timedelta(days=30),
                    'amount': 50000,
                    'status': 'active',
                }
            )
            self.stdout.write('  Created reservation')

        # --- Assign images to ALL plots from landImage/ ---
        import pathlib
        land_dir = settings.BASE_DIR / 'landImage'
        available_imgs = sorted([
            f for f in land_dir.iterdir()
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ]) if land_dir.exists() else []
        plot_image_added = 0
        if available_imgs:
            for i, plot in enumerate(Plot.objects.all()):
                img_name = available_imgs[i % len(available_imgs)].name
                _, created = PlotImage.objects.get_or_create(
                    plot=plot,
                    image='plots/' + img_name,
                    defaults={
                        'caption': f'{plot.project.name} - Plot {plot.plot_number}',
                        'is_primary': True,
                    }
                )
                if created:
                    plot_image_added += 1
        self.stdout.write(f'  Added {plot_image_added} plot images to {Plot.objects.count()} plots')

        # --- Seed Notifications ---
        from apps.notifications.models import Notification
        notif_data = [
            (customers[0].user, 'payment', 'Payment Confirmed', 'Your payment of KSh 100,000 (REC-2024-001) has been confirmed.', '/payments/'),
            (customers[0].user, 'sale', 'Plot Allocated', 'Plot PRJ-A-001 has been allocated to you.', '/sales/'),
            (customers[0].user, 'document', 'New Document', 'A new document "Sale Agreement" has been uploaded.', '/documents/'),
            (customers[1].user, 'support', 'Reservation Submitted', 'Your booking for plot has been submitted and is pending confirmation.', '/sales/'),
            (customers[2].user, 'document', 'New Document', 'A new document "Title Deed" has been uploaded.', '/documents/'),
        ]
        notif_count = 0
        for recipient, ntype, title, msg, link in notif_data:
            _, created = Notification.objects.get_or_create(
                recipient=recipient,
                title=title,
                defaults={'notification_type': ntype, 'message': msg, 'link': link}
            )
            if created:
                notif_count += 1
        self.stdout.write(f'  Created {notif_count} notifications')

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
        self.stdout.write('')
        self.stdout.write('Staff login:     username: admin  |  password: admin123')
        self.stdout.write('Customer login:  username: john   |  password: customer123')
        self.stdout.write('                 username: jane   |  password: customer123')
        self.stdout.write('                 username: peter  |  password: customer123')
