"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { profileAPI, type UserProfile, type UpdateProfileRequest, type Goal, type DietType } from "@/lib/api";
import { Button } from "@/app/recipe_configure/components/ui/button";
import { Input } from "@/app/recipe_configure/components/ui/input";
import { Label } from "@/app/recipe_configure/components/ui/label";
import { Textarea } from "@/app/recipe_configure/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/recipe_configure/components/ui/card";
import { Checkbox } from "@/app/recipe_configure/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/app/recipe_configure/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/app/recipe_configure/components/ui/avatar";
import { Camera, Save, Loader2, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/app/recipe_configure/components/ui/sonner";

export default function ProfilePage() {
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [selectedGoals, setSelectedGoals] = useState<number[]>([]);
  const [diet, setDiet] = useState<number | null>(null);
  const [description, setDescription] = useState<string>('');
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [profileImagePreview, setProfileImagePreview] = useState<string | null>(null);

  // Options from API
  const [goalOptions, setGoalOptions] = useState<Goal[]>([]);
  const [dietOptions, setDietOptions] = useState<DietType[]>([]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated) {
      loadOptions();
      loadProfile();
    }
  }, [authLoading, isAuthenticated, router]);

  const loadOptions = async () => {
    try {
      const [goals, dietTypes] = await Promise.all([
        profileAPI.getGoals(),
        profileAPI.getDietTypes(),
      ]);
      setGoalOptions(goals);
      setDietOptions(dietTypes);
    } catch (error) {
      console.error('Error loading options:', error);
      toast.error('Failed to load options');
    }
  };

  const loadProfile = async () => {
    try {
      setLoading(true);
      const profileData = await profileAPI.getProfile();
      setProfile(profileData);
      // Extract goal IDs from goals array (goals is array of Goal objects from API)
      const goalIds = profileData.goals?.map((g: any) => typeof g === 'object' ? g.id : g) || [];
      setSelectedGoals(goalIds);
      // Extract diet ID (diet is DietType object from API)
      const dietId = profileData.diet ? (typeof profileData.diet === 'object' ? profileData.diet.id : profileData.diet) : null;
      setDiet(dietId);
      setDescription(profileData.description || '');
      if (profileData.profile_image_url) {
        setProfileImagePreview(profileData.profile_image_url);
      }
    } catch (error: any) {
      console.error('Error loading profile:', error);
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProfileImage(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGoalToggle = (goalId: number) => {
    setSelectedGoals(prev => {
      if (prev.includes(goalId)) {
        return prev.filter(g => g !== goalId);
      } else {
        return [...prev, goalId];
      }
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      const updateData: UpdateProfileRequest = {
        goal_ids: selectedGoals,
        diet_id: diet,
        description: description,
      };

      if (profileImage) {
        updateData.profile_image = profileImage;
      }

      console.log('Sending profile update:', updateData);
      const updatedProfile = await profileAPI.updateProfile(updateData);
      console.log('Profile updated successfully:', updatedProfile);
      setProfile(updatedProfile);

      if (updatedProfile.profile_image_url) {
        setProfileImagePreview(updatedProfile.profile_image_url);
      }
      setProfileImage(null); // Clear file input after save

      toast.success('Profile updated successfully!');
    } catch (error: any) {
      console.error('Error updating profile:', error);
      console.error('Error details:', {
        message: error.message,
        statusCode: error.statusCode,
        fieldErrors: error.fieldErrors
      });

      // Show more detailed error message
      if (error.fieldErrors) {
        const errorMessages = Object.entries(error.fieldErrors)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join('\n');
        toast.error(errorMessages);
      } else {
        toast.error(error.message || 'Failed to update profile');
      }
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Toaster />
      {/* Back Button */}
      <div className="mb-4">
        <Button
          variant="outline"
          onClick={() => router.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>My Profile</CardTitle>
          <CardDescription>
            Manage your profile information, goals, and preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Profile Image Section */}
          <div className="flex flex-col items-center space-y-4">
            <Avatar className="h-32 w-32">
              <AvatarImage src={profileImagePreview || undefined} alt={user?.email || 'Profile'} />
              <AvatarFallback className="text-2xl bg-gray-400 text-white font-semibold">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col items-center space-y-2">
              <Label htmlFor="profile-image" className="cursor-pointer">
                <Button variant="outline" asChild>
                  <span>
                    <Camera className="mr-2 h-4 w-4" />
                    Change Photo
                  </span>
                </Button>
              </Label>
              <Input
                id="profile-image"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
              />
              {profileImage && (
                <p className="text-sm text-muted-foreground">
                  {profileImage.name}
                </p>
              )}
            </div>
          </div>

          {/* User Info (Read-only) */}
          <div>
            <Label>Email</Label>
            <Input value={profile?.email || user?.email || ''} disabled />
          </div>

          {/* Goals Section */}
          <div>
            <Label className="text-base font-semibold mb-3 block">Goals</Label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {goalOptions.map((goal) => (
                <div key={goal.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={`goal-${goal.id}`}
                    checked={selectedGoals.includes(goal.id)}
                    onCheckedChange={() => handleGoalToggle(goal.id)}
                  />
                  <Label
                    htmlFor={`goal-${goal.id}`}
                    className="text-sm font-normal cursor-pointer"
                  >
                    {goal.name}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Diet Selection */}
          <div>
            <Label htmlFor="diet" className="text-base font-semibold mb-2 block">
              Diet Preference
            </Label>
            <Select
              value={diet?.toString() || 'none'}
              onValueChange={(value) => setDiet(value === 'none' ? null : parseInt(value))}
            >
              <SelectTrigger id="diet">
                <SelectValue placeholder="Select your diet preference" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No Specific Diet</SelectItem>
                {dietOptions.map((option) => (
                  <SelectItem key={option.id} value={option.id.toString()}>
                    {option.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description" className="text-base font-semibold mb-2 block">
              Description & Goals
            </Label>
            <Textarea
              id="description"
              placeholder="Tell us about your goals, preferences, and what you're looking to achieve..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
            />
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-black text-white hover:bg-gray-800 transition-colors"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
