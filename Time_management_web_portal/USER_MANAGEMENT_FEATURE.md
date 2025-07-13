# User Management Feature

## Overview
A comprehensive user management system has been added to the Time Management Portal, allowing administrators to manage user accounts, roles, and permissions.

## Features

### 🔍 **Search and Filter**
- **Username Search**: Search by login name or full name
- **Account Type Filter**: Filter users by their account type/role
- **Real-time Results**: Dynamic filtering with instant feedback

### ➕ **Add New Users**
- **Complete User Creation**: Add new users with all required information
- **Role Assignment**: Assign account types during creation
- **Password Setup**: Set initial passwords for new accounts
- **Email Validation**: Built-in email format validation

### ✏️ **Edit Existing Users**
- **Pre-filled Forms**: Edit modal auto-populates with current user data
- **Selective Updates**: Update any field independently
- **Password Management**: Optional password updates (leave blank to keep existing)
- **Username Uniqueness**: Prevents duplicate usernames

### 🗑️ **Delete Users**
- **Confirmation Dialog**: Requires confirmation before deletion
- **Safety Checks**: Prevents users from deleting their own accounts
- **Clear Warnings**: Shows exactly which user will be deleted

## Access Control

### **Administrator Only**
- Only users with "Administrator" account type can access user management
- Non-administrators are redirected with appropriate error messages
- Session-based authentication ensures secure access

### **Navigation**
- **Menu Item**: "User Management" appears in navigation for administrators only
- **Direct Access**: Available at `/users` route
- **Integrated UI**: Consistent styling with rest of the application

## Technical Implementation

### **Files Created/Modified**
1. **`templates/user_management.html`** - Main user interface
2. **`routes/user_routes.py`** - Backend route handlers (updated)
3. **`templates/base.html`** - Navigation menu (updated)
4. **`dbQueryIncident.py`** - Database view references (updated)

### **Database Integration**
- **Account_View**: Uses the proper database view for user data
- **Account_Type**: Integrates with account type lookup table
- **Login_Account**: Full CRUD operations on user accounts

### **Routes Added**
- `GET /users` - Display user management interface
- `GET /get_user/<user_id>` - Fetch user details for editing
- `POST /create_user` - Create new user account
- `POST /update_user` - Update existing user account
- `POST /delete_user` - Delete user account

## User Interface Features

### **Responsive Design**
- **Mobile Friendly**: Works on all screen sizes
- **Consistent Styling**: Matches existing application theme
- **Modern UI**: Clean, professional appearance

### **Interactive Elements**
- **Draggable Modals**: User can reposition edit/add dialogs
- **Form Validation**: Client-side and server-side validation
- **Status Messages**: Success/error feedback for all operations
- **Confirmation Dialogs**: Safe deletion with user confirmation

### **Data Display**
- **Sortable Table**: Clear presentation of user data
- **Action Buttons**: Intuitive edit/delete buttons for each user
- **Filter Display**: Shows active search criteria
- **Empty States**: Graceful handling of no results

## Security Features

### **Input Validation**
- **Required Fields**: Ensures all necessary data is provided
- **Email Format**: Validates email address format
- **Password Rules**: Enforces password requirements for new users
- **Username Uniqueness**: Prevents duplicate login names

### **Access Protection**
- **Session Verification**: All routes check for valid login
- **Role Authorization**: Administrator-only access enforcement
- **Self-Protection**: Users cannot delete their own accounts
- **Error Handling**: Graceful handling of database errors

## Usage Instructions

### **For Administrators**
1. **Access**: Click "User Management" in the navigation menu
2. **Search**: Use the search box to find specific users
3. **Filter**: Select account type from dropdown to filter results
4. **Add User**: Click "Add New User" button, fill form, submit
5. **Edit User**: Click "Edit" button on any user row, modify fields, save
6. **Delete User**: Click "Delete" button, confirm in dialog

### **Search Tips**
- **Username Search**: Searches both login name and full name
- **Partial Matching**: Type partial names for broader results
- **Clear Filters**: Use "Clear" button to reset all filters
- **Combine Filters**: Use username search with account type filter

## Integration Notes

### **Database Structure**
- Uses existing `Login_Account` table
- Leverages `Account_Type` table for role management
- Integrates with `Account_View` for enhanced user data

### **Session Management**
- Maintains existing session handling
- Preserves current authentication flow
- Compatible with existing user roles

### **Error Handling**
- Comprehensive error catching and user feedback
- Database connection management
- Graceful degradation on failures

---

*This feature enhances the Time Management Portal by providing complete user lifecycle management while maintaining security and usability standards.*
