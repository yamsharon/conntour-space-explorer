import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

const Layout: React.FC = () => {

  // This function is used to style the active and inactive nav links
  const navLinkClassName = ({ isActive }: { isActive: boolean }) => {
    return `inline-block py-3 border-b-2 ${
      isActive
        ? 'border-blue-500 text-blue-600 font-semibold'
        : 'border-transparent text-gray-600 hover:text-gray-800'
    }`;
  };

  return (
    <div className="container mx-auto px-4">
      <div className="sticky top-0 z-20 mb-8 bg-gray-100 pb-2 shadow-none -mx-4 px-4">
        <h1 className="pt-8 text-3xl font-bold mb-2">NASA Space Images</h1>
        <nav className="border-b border-gray-200">
          <ul className="flex space-x-6">
            <li>
              <NavLink
                to="/"
                end
                className={navLinkClassName}
              >
                Browse
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/search"
                className={navLinkClassName}
              >
                Search
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/history"
                className={navLinkClassName}
              >
                History
              </NavLink>
            </li>
          </ul>
        </nav>
      </div>

      <Outlet />
    </div>
  );
};

export default Layout;