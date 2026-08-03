/* =====================================================
   ASAT – App Entry Point & Router Configuration
   ===================================================== */

import './style.css';
import './animations.css';

import { route, startRouter } from './router.js';

// Pages – Student Flow
import { LandingPage }           from './pages/Landing.js';
import { StudentRegisterPage }   from './pages/StudentRegister.js';
import { InstructionsPage }      from './pages/Instructions.js';
import { PracticePage }          from './pages/Practice.js';
import { ModuleSustainedPage }   from './pages/ModuleSustained.js';
import { ModuleSelectivePage }   from './pages/ModuleSelective.js';
import { ModuleDividedPage }     from './pages/ModuleDivided.js';
import { ModuleExecutivePage }   from './pages/ModuleExecutive.js';
import { ResultsPage }           from './pages/Results.js';

// Pages – Faculty Flow
import { FacultyHomePage }       from './pages/FacultyHome.js';
import { FacultyRegisterPage }   from './pages/FacultyRegister.js';
import { FacultyLoginPage }      from './pages/FacultyLogin.js';
import { FacultyDashboardPage }  from './pages/FacultyDashboard.js';
import { StudentDetailPage }     from './pages/StudentDetail.js';

/* ── Register all routes ── */

// Student flow
route('/',                    (el)         => LandingPage(el));
route('/register',            (el)         => StudentRegisterPage(el));
route('/instructions',        (el)         => InstructionsPage(el));
route('/practice',            (el)         => PracticePage(el));
route('/module/sustained',    (el)         => ModuleSustainedPage(el));
route('/module/selective',    (el)         => ModuleSelectivePage(el));
route('/module/divided',      (el)         => ModuleDividedPage(el));
route('/module/executive',    (el)         => ModuleExecutivePage(el));
route('/results',             (el)         => ResultsPage(el));

// Faculty flow
route('/faculty',             (el)         => FacultyHomePage(el));
route('/faculty/register',    (el)         => FacultyRegisterPage(el));
route('/faculty/login',       (el)         => FacultyLoginPage(el));
route('/faculty/dashboard',   (el)         => FacultyDashboardPage(el));
route('/faculty/student/:id', (el, params) => StudentDetailPage(el, params));

// Also match /about → redirect to landing with about section
route('/about', (el) => LandingPage(el));

/* ── Start the router ── */
startRouter();
