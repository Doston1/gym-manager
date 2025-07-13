from nicegui import ui, app
import requests
from frontend.config import API_HOST, API_PORT  # Import environment variables
import httpx
from frontend.components.navbar import create_navbar, apply_page_style, get_current_user, logout

async def home_page(user_id: str = None):
    # Apply consistent page styling
    apply_page_style()

    ui.query('.nicegui-content').classes('items-center')
    
    # Create navbar and get user
    user = await create_navbar()
    if user:
        # Fetch full user details from the backend
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://{API_HOST}:{API_PORT}/users/{user["auth_id"]}')
            if response.status_code == 200:
                user = response.json()
                if user.get("first_name") == "temp_first_name" and user.get("last_name") == "temp_last_name":
                    # If the user is a temporary user, redirect to full details page
                    ui.navigate.to('/full-details')
                    return

    # Hero Section
    with ui.column().classes('w-full min-h-screen'):
        # Main Hero Banner
        with ui.card().classes('w-full p-0 bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 rounded-2xl shadow-2xl border border-blue-500/30 overflow-hidden'):
            # Hero Content
            with ui.column().classes('w-full p-12 text-center relative'):
                # Animated background elements
                ui.add_head_html('''
                    <style>
                        @keyframes pulse-glow {
                            0%, 100% { opacity: 0.5; transform: scale(1); }
                            50% { opacity: 1; transform: scale(1.05); }
                        }
                        @keyframes float {
                            0%, 100% { transform: translateY(0px); }
                            50% { transform: translateY(-10px); }
                        }
                        .hero-glow { animation: pulse-glow 3s ease-in-out infinite; }
                        .float-animation { animation: float 4s ease-in-out infinite; }
                        .gradient-text {
                            background: linear-gradient(45deg, #60a5fa, #a78bfa, #f472b6);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                        }
                        .glass-effect {
                            background: rgba(255, 255, 255, 0.1);
                            backdrop-filter: blur(10px);
                            border: 1px solid rgba(255, 255, 255, 0.2);
                        }
                    </style>
                ''')
                
                # Logo/Icon with glow effect
                with ui.column().classes('items-center mb-8'):
                    ui.icon('fitness_center').classes('text-8xl text-blue-300 hero-glow mb-4')
                    
                if user:
                    # Personalized welcome for logged-in users
                    ui.label(f'Welcome Back, {user.get("first_name", "User")}!').classes('text-5xl font-bold gradient-text mb-4')
                    ui.label('Ready to crush your fitness goals today?').classes('text-xl text-blue-200 mb-8 font-light')
                    
                    # Quick action buttons for logged-in users
                    with ui.row().classes('gap-4 justify-center mb-8'):
                        ui.button('My Dashboard', on_click=lambda: ui.navigate.to('/myprofile')).classes(
                            'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 '
                            'text-white px-8 py-4 rounded-xl font-bold text-lg shadow-xl transform hover:scale-105 transition-all duration-300'
                        )
                        ui.button('Browse Classes', on_click=lambda: ui.navigate.to('/classes')).classes(
                            'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 '
                            'text-white px-8 py-4 rounded-xl font-bold text-lg shadow-xl transform hover:scale-105 transition-all duration-300'
                        )
                else:
                    # Hero content for non-logged-in users
                    ui.label('FITZONE ELITE').classes('text-7xl font-black gradient-text mb-2 tracking-wide')
                    ui.label('Transform Your Body, Elevate Your Mind').classes('text-2xl text-blue-200 mb-6 font-light italic')
                    ui.label('Experience the ultimate fitness journey with state-of-the-art equipment, expert trainers, and a community that pushes you to excel.').classes('text-lg text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed')
                    
                    # CTA buttons
                    with ui.row().classes('gap-6 justify-center mb-8'):
                        ui.button('START YOUR JOURNEY', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes(
                            'bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 '
                            'text-white px-12 py-5 rounded-xl font-bold text-xl shadow-2xl transform hover:scale-110 transition-all duration-300 '
                            'border-2 border-orange-400 hover:border-red-400'
                        )
                        ui.button('EXPLORE CLASSES', on_click=lambda: ui.navigate.to('/classes')).classes(
                            'bg-transparent border-2 border-blue-400 text-blue-300 hover:bg-blue-500 hover:text-white '
                            'px-10 py-5 rounded-xl font-bold text-xl shadow-xl transform hover:scale-105 transition-all duration-300'
                        )
                
                # Stats section
                with ui.row().classes('gap-12 justify-center mt-12'):
                    # Stat 1
                    with ui.column().classes('text-center glass-effect p-6 rounded-xl'):
                        ui.label('2000+').classes('text-4xl font-bold text-orange-400 mb-2')
                        ui.label('Active Members').classes('text-gray-300 font-medium')
                    
                    # Stat 2
                    with ui.column().classes('text-center glass-effect p-6 rounded-xl'):
                        ui.label('50+').classes('text-4xl font-bold text-green-400 mb-2')
                        ui.label('Expert Trainers').classes('text-gray-300 font-medium')
                    
                    # Stat 3
                    with ui.column().classes('text-center glass-effect p-6 rounded-xl'):
                        ui.label('100+').classes('text-4xl font-bold text-purple-400 mb-2')
                        ui.label('Weekly Classes').classes('text-gray-300 font-medium')
                    
                    # Stat 4
                    with ui.column().classes('text-center glass-effect p-6 rounded-xl'):
                        ui.label('24/7').classes('text-4xl font-bold text-blue-400 mb-2')
                        ui.label('Access Hours').classes('text-gray-300 font-medium')

    # Features Section
    with ui.card().classes('w-full mt-8 p-12 bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700'):
        ui.label('Why Choose FitZone Elite?').classes('text-4xl font-bold text-center mb-12 gradient-text')
        
        with ui.grid(columns=3).classes('w-full gap-8'):
            # Feature 1
            with ui.card().classes('p-8 bg-gradient-to-br from-blue-800 to-blue-900 rounded-xl border border-blue-600 hover:shadow-blue-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('fitness_center').classes('text-5xl text-blue-300 mb-4 float-animation')
                ui.label('Premium Equipment').classes('text-2xl font-bold text-blue-200 mb-4')
                ui.label('State-of-the-art machines and free weights from top brands. Our equipment is regularly maintained and updated to provide the best workout experience.').classes('text-gray-300 leading-relaxed')
            
            # Feature 2
            with ui.card().classes('p-8 bg-gradient-to-br from-green-800 to-green-900 rounded-xl border border-green-600 hover:shadow-green-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('groups').classes('text-5xl text-green-300 mb-4 float-animation')
                ui.label('Expert Trainers').classes('text-2xl font-bold text-green-200 mb-4')
                ui.label('Certified professionals with years of experience in fitness, nutrition, and wellness. Get personalized guidance to achieve your goals safely and effectively.').classes('text-gray-300 leading-relaxed')
            
            # Feature 3
            with ui.card().classes('p-8 bg-gradient-to-br from-purple-800 to-purple-900 rounded-xl border border-purple-600 hover:shadow-purple-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('schedule').classes('text-5xl text-purple-300 mb-4 float-animation')
                ui.label('Flexible Schedule').classes('text-2xl font-bold text-purple-200 mb-4')
                ui.label('Classes and training sessions available throughout the day to fit your busy lifestyle. Book online, cancel easily, and track your progress.').classes('text-gray-300 leading-relaxed')
            
            # Feature 4
            with ui.card().classes('p-8 bg-gradient-to-br from-orange-800 to-orange-900 rounded-xl border border-orange-600 hover:shadow-orange-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('restaurant').classes('text-5xl text-orange-300 mb-4 float-animation')
                ui.label('Nutrition Support').classes('text-2xl font-bold text-orange-200 mb-4')
                ui.label('Comprehensive nutrition guidance and meal planning to complement your fitness journey. Our experts help you fuel your body for optimal results.').classes('text-gray-300 leading-relaxed')
            
            # Feature 5
            with ui.card().classes('p-8 bg-gradient-to-br from-red-800 to-red-900 rounded-xl border border-red-600 hover:shadow-red-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('analytics').classes('text-5xl text-red-300 mb-4 float-animation')
                ui.label('Progress Tracking').classes('text-2xl font-bold text-red-200 mb-4')
                ui.label('Advanced tracking tools to monitor your workouts, set goals, and visualize your progress. Stay motivated with detailed analytics and achievements.').classes('text-gray-300 leading-relaxed')
            
            # Feature 6
            with ui.card().classes('p-8 bg-gradient-to-br from-cyan-800 to-cyan-900 rounded-xl border border-cyan-600 hover:shadow-cyan-500/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105'):
                ui.icon('spa').classes('text-5xl text-cyan-300 mb-4 float-animation')
                ui.label('Wellness Center').classes('text-2xl font-bold text-cyan-200 mb-4')
                ui.label('Complete wellness facility with sauna, steam room, massage therapy, and recovery zones. Take care of your body inside and out.').classes('text-gray-300 leading-relaxed')

    # Services Section
    with ui.card().classes('w-full mt-8 p-12 bg-gradient-to-br from-indigo-900 to-purple-900 rounded-2xl shadow-2xl border border-indigo-600'):
        ui.label('Our Services').classes('text-4xl font-bold text-center mb-12 text-white')
        
        with ui.row().classes('w-full gap-8 justify-center'):
            # Service 1
            with ui.column().classes('flex-1 text-center'):
                with ui.card().classes('p-8 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300'):
                    ui.icon('school').classes('text-6xl text-yellow-300 mb-4')
                    ui.label('Personal Training').classes('text-2xl font-bold text-white mb-4')
                    ui.label('One-on-one sessions with certified trainers').classes('text-gray-300 mb-6')
                    ui.button('Learn More', on_click=lambda: ui.navigate.to('/about')).classes(
                        'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 '
                        'text-white px-6 py-3 rounded-lg font-semibold shadow-lg transform hover:scale-105 transition-all duration-200'
                    )
            
            # Service 2
            with ui.column().classes('flex-1 text-center'):
                with ui.card().classes('p-8 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300'):
                    ui.icon('groups_2').classes('text-6xl text-pink-300 mb-4')
                    ui.label('Group Classes').classes('text-2xl font-bold text-white mb-4')
                    ui.label('Fun and motivating group fitness sessions').classes('text-gray-300 mb-6')
                    ui.button('View Classes', on_click=lambda: ui.navigate.to('/classes')).classes(
                        'bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 '
                        'text-white px-6 py-3 rounded-lg font-semibold shadow-lg transform hover:scale-105 transition-all duration-200'
                    )
            
            # Service 3
            with ui.column().classes('flex-1 text-center'):
                with ui.card().classes('p-8 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-300'):
                    ui.icon('assignment').classes('text-6xl text-green-300 mb-4')
                    ui.label('Training Plans').classes('text-2xl font-bold text-white mb-4')
                    ui.label('Customized workout plans for your goals').classes('text-gray-300 mb-6')
                    ui.button('Explore Plans', on_click=lambda: ui.navigate.to('/training-plans')).classes(
                        'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 '
                        'text-white px-6 py-3 rounded-lg font-semibold shadow-lg transform hover:scale-105 transition-all duration-200'
                    )

    # Testimonials Section (if not logged in)
    if not user:
        with ui.card().classes('w-full mt-8 p-12 bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-gray-700'):
            ui.label('What Our Members Say').classes('text-4xl font-bold text-center mb-12 text-blue-300')
            
            with ui.row().classes('w-full gap-8'):
                # Testimonial 1
                with ui.card().classes('flex-1 p-8 bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-xl border border-blue-600/30'):
                    ui.icon('format_quote').classes('text-4xl text-blue-300 mb-4')
                    ui.label('"FitZone Elite completely transformed my fitness journey. The trainers are incredible and the equipment is top-notch!"').classes('text-gray-300 italic text-lg mb-4 leading-relaxed')
                    ui.label('- Sarah M., Member since 2023').classes('text-blue-300 font-semibold')
                
                # Testimonial 2
                with ui.card().classes('flex-1 p-8 bg-gradient-to-br from-green-900/50 to-teal-900/50 rounded-xl border border-green-600/30'):
                    ui.icon('format_quote').classes('text-4xl text-green-300 mb-4')
                    ui.label('"The variety of classes keeps me motivated. I\'ve achieved goals I never thought possible!"').classes('text-gray-300 italic text-lg mb-4 leading-relaxed')
                    ui.label('- Mike R., Member since 2022').classes('text-green-300 font-semibold')
                
                # Testimonial 3
                with ui.card().classes('flex-1 p-8 bg-gradient-to-br from-orange-900/50 to-red-900/50 rounded-xl border border-orange-600/30'):
                    ui.icon('format_quote').classes('text-4xl text-orange-300 mb-4')
                    ui.label('"Best investment I\'ve made for my health. The community here is amazing and supportive!"').classes('text-gray-300 italic text-lg mb-4 leading-relaxed')
                    ui.label('- Jessica L., Member since 2021').classes('text-orange-300 font-semibold')

    # Final CTA Section
    if not user:
        with ui.card().classes('w-full mt-8 p-12 bg-gradient-to-br from-purple-900 to-indigo-900 rounded-2xl shadow-2xl border border-purple-600 text-center'):
            ui.label('Ready to Start Your Transformation?').classes('text-4xl font-bold text-white mb-6')
            ui.label('Join thousands of members who have already transformed their lives at FitZone Elite').classes('text-xl text-purple-200 mb-8')
            
            with ui.row().classes('gap-6 justify-center'):
                ui.button('JOIN NOW - SPECIAL OFFER', on_click=lambda: ui.navigate.to(f'http://{API_HOST}:{API_PORT}/login')).classes(
                    'bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 '
                    'text-white px-12 py-5 rounded-xl font-bold text-xl shadow-2xl transform hover:scale-110 transition-all duration-300 '
                    'border-2 border-orange-400 hover:border-red-400 animate-pulse'
                )
                ui.button('SCHEDULE A TOUR', on_click=lambda: ui.navigate.to('/about')).classes(
                    'bg-transparent border-2 border-white text-white hover:bg-white hover:text-purple-900 '
                    'px-10 py-5 rounded-xl font-bold text-xl shadow-xl transform hover:scale-105 transition-all duration-300'
                )

    

def login():
    auth0_url = f"http://{API_HOST}:{API_PORT}/login"
    ui.navigate.to(auth0_url, new_tab=False)
